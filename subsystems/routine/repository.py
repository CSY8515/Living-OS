from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from subsystems.database.engines.component import ComponentDatabaseAdapter
from subsystems.foundation.engines.time import utc_now_iso

if TYPE_CHECKING:
    from subsystems.database.subsystem import DatabaseSubsystem


SCHEMA_VERSION = 1


class RoutineRepository(ComponentDatabaseAdapter):
    def __init__(self, database_path: Path, foundation: DatabaseSubsystem | None = None) -> None:
        super().__init__(database_path, component_id="SUB-ROUTINE", display_name="Routine Subsystem", foundation=foundation)

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connections.transaction() as c:
            c.executescript("""
                CREATE TABLE IF NOT EXISTS routine_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL,updated_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS routines(
                    routine_id TEXT PRIMARY KEY,name TEXT NOT NULL,description TEXT NOT NULL,category TEXT NOT NULL,
                    frequency TEXT NOT NULL,schedule_rule TEXT NOT NULL,priority INTEGER NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('DRAFT','ACTIVE','PAUSED','COMPLETED','ARCHIVED')),
                    start_date TEXT NOT NULL,end_date TEXT NOT NULL,last_executed_at TEXT,next_due_at TEXT,
                    completion_count INTEGER NOT NULL,failure_count INTEGER NOT NULL,streak INTEGER NOT NULL,
                    created_at TEXT NOT NULL,updated_at TEXT NOT NULL,metadata_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_routines_status_due ON routines(status,next_due_at);
                CREATE TABLE IF NOT EXISTS routine_executions(
                    execution_id TEXT PRIMARY KEY,routine_id TEXT NOT NULL REFERENCES routines(routine_id),
                    scheduled_at TEXT NOT NULL,executed_at TEXT,result TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('PENDING','COMPLETED','FAILED','SKIPPED')),
                    note TEXT NOT NULL,duration INTEGER NOT NULL,created_at TEXT NOT NULL,metadata_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_routine_executions ON routine_executions(routine_id,scheduled_at,status);
                CREATE TABLE IF NOT EXISTS routine_migrations(migration_id TEXT PRIMARY KEY,schema_version INTEGER NOT NULL,status TEXT NOT NULL,started_at TEXT NOT NULL,completed_at TEXT NOT NULL,error TEXT NOT NULL DEFAULT '');
            """)
            now = utc_now_iso()
            c.execute("INSERT INTO routine_meta VALUES('schema_version',?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at", (str(SCHEMA_VERSION),now))
            c.execute("INSERT OR IGNORE INTO routine_migrations VALUES(?,?,?,?,?,?)", ("routine-schema-v1",1,"APPLIED",now,now,""))
        self.register_contract(schema_version=1,migration_id="routine-schema-v1")

    def create(self,p:dict[str,Any])->dict[str,Any]:
        with self.transaction() as c: c.execute("INSERT INTO routines VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", self._values(p))
        return self.get(p["routine_id"]) or {}
    def get(self,routine_id:str)->dict[str,Any]|None:
        rows=self.query_rows("SELECT * FROM routines WHERE routine_id=?",(routine_id,)); return self._decode(rows[0]) if rows else None
    def update(self,routine_id:str,p:dict[str,Any])->dict[str,Any]:
        with self.transaction() as c:
            cursor=c.execute("""UPDATE routines SET name=?,description=?,category=?,frequency=?,schedule_rule=?,priority=?,status=?,start_date=?,end_date=?,last_executed_at=?,next_due_at=?,completion_count=?,failure_count=?,streak=?,created_at=?,updated_at=?,metadata_json=? WHERE routine_id=?""",(*self._values(p)[1:],routine_id))
            if cursor.rowcount!=1: raise KeyError(routine_id)
        return self.get(routine_id) or {}
    def list(self,*,status:str|None=None,include_archived:bool=False,limit:int=200)->list[dict[str,Any]]:
        clauses=[];params=[]
        if not include_archived: clauses.append("status!='ARCHIVED'")
        if status: clauses.append("status=?");params.append(status)
        sql="SELECT * FROM routines"+(" WHERE "+" AND ".join(clauses) if clauses else "")+" ORDER BY priority DESC,next_due_at,updated_at DESC LIMIT ?";params.append(max(1,min(int(limit),1000)))
        return [self._decode(r) for r in self.query_rows(sql,tuple(params))]
    def add_execution(self,p:dict[str,Any])->dict[str,Any]:
        values=(p["execution_id"],p["routine_id"],p["scheduled_at"],p.get("executed_at"),p.get("result",""),p.get("status","PENDING"),p.get("note",""),int(p.get("duration",0)),p["created_at"],json.dumps(p.get("metadata",{}),ensure_ascii=False,sort_keys=True))
        with self.transaction() as c: c.execute("INSERT INTO routine_executions VALUES(?,?,?,?,?,?,?,?,?,?)",values)
        return self.execution(p["execution_id"]) or {}
    def execution(self,execution_id:str)->dict[str,Any]|None:
        rows=self.query_rows("SELECT * FROM routine_executions WHERE execution_id=?",(execution_id,)); return self._decode_execution(rows[0]) if rows else None
    def update_execution(self,execution_id:str,**changes:Any)->dict[str,Any]:
        allowed={"executed_at","result","status","note","duration","metadata"}; fields=[];params=[]
        for key,value in changes.items():
            if key not in allowed: continue
            column="metadata_json" if key=="metadata" else key; fields.append(f"{column}=?");params.append(json.dumps(value,ensure_ascii=False,sort_keys=True) if key=="metadata" else value)
        if not fields: return self.execution(execution_id) or {}
        params.append(execution_id)
        with self.transaction() as c:
            if c.execute(f"UPDATE routine_executions SET {','.join(fields)} WHERE execution_id=?",tuple(params)).rowcount!=1: raise KeyError(execution_id)
        return self.execution(execution_id) or {}
    def process_execution(self,execution_id:str,execution_changes:dict[str,Any],routine_id:str,routine_payload:dict[str,Any])->dict[str,Any]:
        fields=[];params=[]
        for key,value in execution_changes.items():
            column="metadata_json" if key=="metadata" else key;fields.append(f"{column}=?");params.append(json.dumps(value,ensure_ascii=False,sort_keys=True) if key=="metadata" else value)
        params.extend((execution_id,"PENDING"))
        with self.transaction() as c:
            if c.execute(f"UPDATE routine_executions SET {','.join(fields)} WHERE execution_id=? AND status=?",tuple(params)).rowcount!=1: raise ValueError("Execution is missing or already processed.")
            values=self._values(routine_payload)
            if c.execute("""UPDATE routines SET name=?,description=?,category=?,frequency=?,schedule_rule=?,priority=?,status=?,start_date=?,end_date=?,last_executed_at=?,next_due_at=?,completion_count=?,failure_count=?,streak=?,created_at=?,updated_at=?,metadata_json=? WHERE routine_id=?""",(*values[1:],routine_id)).rowcount!=1: raise KeyError(routine_id)
        return self.execution(execution_id) or {}
    def executions(self,routine_id:str|None=None,limit:int=200)->list[dict[str,Any]]:
        sql="SELECT * FROM routine_executions";params=[]
        if routine_id: sql+=" WHERE routine_id=?";params.append(routine_id)
        sql+=" ORDER BY scheduled_at DESC LIMIT ?";params.append(max(1,min(int(limit),1000)))
        return [self._decode_execution(r) for r in self.query_rows(sql,tuple(params))]
    def health(self)->dict[str,Any]:
        if not self.initialized:return {"status":"READY","initialized":False,"schema_version":1}
        rows=self.query_rows("PRAGMA integrity_check");ok=bool(rows) and next(iter(rows[0].values()))=="ok";return {"status":"HEALTHY" if ok else "DEGRADED","initialized":True,"schema_version":1,"integrity":"ok" if ok else "failed"}
    @staticmethod
    def _values(p:dict[str,Any])->tuple[Any,...]: return (p["routine_id"],p["name"],p.get("description",""),p.get("category","General"),p.get("frequency","DAILY"),p.get("schedule_rule",""),int(p.get("priority",3)),p.get("status","DRAFT"),p.get("start_date",""),p.get("end_date",""),p.get("last_executed_at"),p.get("next_due_at"),int(p.get("completion_count",0)),int(p.get("failure_count",0)),int(p.get("streak",0)),p["created_at"],p["updated_at"],json.dumps(p.get("metadata",{}),ensure_ascii=False,sort_keys=True))
    @staticmethod
    def _decode(row:dict[str,Any])->dict[str,Any]: row["metadata"]=json.loads(row.pop("metadata_json"));return row
    @staticmethod
    def _decode_execution(row:dict[str,Any])->dict[str,Any]: row["metadata"]=json.loads(row.pop("metadata_json"));return row
