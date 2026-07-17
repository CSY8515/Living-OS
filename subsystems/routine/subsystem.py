from __future__ import annotations

from collections import Counter
from calendar import monthrange
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from subsystems.foundation.engines.time import utc_now_iso
from subsystems.routine.models import RoutineExecutionRecord, RoutineRecord
from subsystems.routine.repository import RoutineRepository


class RoutineSubsystem:
    subsystem_id="SUB-ROUTINE"; VERSION="1.0.0"
    def __init__(self,root:Path,database_path:Path|None=None,database_foundation:Any=None)->None:
        path=Path(database_path) if database_path else Path(root)/"data"/"routine"/"routine.sqlite3";self.repository=RoutineRepository(path,database_foundation);self.repository.register_contract(schema_version=1,migration_id="routine-schema-v1");self.database_foundation=database_foundation
    @staticmethod
    def calculate_next_due(frequency:str,from_time:str|None=None,schedule_rule:str="")->str:
        base=datetime.fromisoformat(from_time) if from_time else datetime.now(timezone.utc)
        if base.tzinfo is None: base=base.replace(tzinfo=timezone.utc)
        if frequency=="DAILY": due=base+timedelta(days=1)
        elif frequency=="WEEKLY": due=base+timedelta(days=7)
        elif frequency=="MONTHLY":
            year = base.year + (1 if base.month == 12 else 0)
            month = 1 if base.month == 12 else base.month + 1
            due = base.replace(year=year, month=month, day=min(base.day, monthrange(year, month)[1]))
        elif frequency=="INTERVAL":
            try: due=base+timedelta(days=max(1,int(schedule_rule or "1")))
            except ValueError as exc: raise ValueError("INTERVAL schedule_rule must be a number of days.") from exc
        else: raise ValueError(f"Unsupported frequency: {frequency}")
        return due.isoformat()
    def create(self,name:str,**fields:Any)->dict[str,Any]:
        now=utc_now_iso();routine_id=str(fields.pop("routine_id","") or uuid4());frequency=str(fields.get("frequency","DAILY"));status=str(fields.get("status","DRAFT"));fields.setdefault("next_due_at",self.calculate_next_due(frequency,now,str(fields.get("schedule_rule",""))) if status=="ACTIVE" else None);record=RoutineRecord(routine_id=routine_id,name=name,created_at=now,updated_at=now,**fields);result=self.repository.create(record.to_dict());self._record("create",routine_id,"COMPLETED");return result
    def get(self,routine_id:str)->dict[str,Any]|None:return self.repository.get(routine_id)
    def update(self,routine_id:str,**changes:Any)->dict[str,Any]:
        current=self.repository.get(routine_id)
        if current is None:raise KeyError(routine_id)
        p={**current,**changes,"routine_id":routine_id,"updated_at":utc_now_iso()};RoutineRecord(**p).validate();result=self.repository.update(routine_id,p);self._record("update",routine_id,"COMPLETED");return result
    def pause(self,routine_id:str)->dict[str,Any]:return self.update(routine_id,status="PAUSED")
    def archive(self,routine_id:str)->dict[str,Any]:result=self.update(routine_id,status="ARCHIVED");self._record("archive",routine_id,"COMPLETED");return result
    def schedule(self,routine_id:str,scheduled_at:str|None=None)->dict[str,Any]:
        routine=self.repository.get(routine_id)
        if routine is None:raise KeyError(routine_id)
        now=utc_now_iso();execution=RoutineExecutionRecord(execution_id=str(uuid4()),routine_id=routine_id,scheduled_at=scheduled_at or routine.get("next_due_at") or now,created_at=now);result=self.repository.add_execution(execution.to_dict());self._record("schedule",routine_id,"COMPLETED");return result
    def process(self,execution_id:str,status:str,*,result:str="",note:str="",duration:int=0)->dict[str,Any]:
        if status not in {"COMPLETED","FAILED","SKIPPED"}:raise ValueError("Execution outcome must be COMPLETED, FAILED, or SKIPPED.")
        execution=self.repository.execution(execution_id)
        if execution is None:raise KeyError(execution_id)
        if execution["status"]!="PENDING":raise ValueError("Execution has already been processed.")
        routine=self.repository.get(execution["routine_id"])
        if routine is None:raise KeyError(execution["routine_id"])
        now=utc_now_iso()
        changes={"last_executed_at":now,"next_due_at":self.calculate_next_due(routine["frequency"],now,routine["schedule_rule"])}
        if status=="COMPLETED":changes.update(completion_count=routine["completion_count"]+1,streak=routine["streak"]+1)
        elif status=="FAILED":changes.update(failure_count=routine["failure_count"]+1,streak=0)
        routine_payload={**routine,**changes,"routine_id":routine["routine_id"],"updated_at":now};RoutineRecord(**routine_payload).validate()
        updated=self.repository.process_execution(execution_id,{"status":status,"result":result,"note":note,"duration":duration,"executed_at":now},routine["routine_id"],routine_payload)
        self._record(status.lower(),routine["routine_id"],"COMPLETED");return updated
    def complete(self,execution_id:str,**kwargs:Any)->dict[str,Any]:return self.process(execution_id,"COMPLETED",**kwargs)
    def fail(self,execution_id:str,**kwargs:Any)->dict[str,Any]:return self.process(execution_id,"FAILED",**kwargs)
    def skip(self,execution_id:str,**kwargs:Any)->dict[str,Any]:return self.process(execution_id,"SKIPPED",**kwargs)
    def list(self,**filters:Any)->list[dict[str,Any]]:return self.repository.list(**filters)
    def executions(self,**filters:Any)->list[dict[str,Any]]:return self.repository.executions(**filters)
    def due(self,at:str|None=None)->list[dict[str,Any]]:
        cutoff=at or utc_now_iso();return [r for r in self.list(status="ACTIVE",limit=1000) if r.get("next_due_at") and r["next_due_at"]<=cutoff]
    def health(self)->dict[str,Any]:return self.repository.health()
    def management_summary(self)->dict[str,Any]:
        routines=self.list(include_archived=True,limit=1000);history=self.executions(limit=1000);control=[e for e in (self.database_foundation.execution_records(500) if self.database_foundation else []) if e.get("subsystem")==self.subsystem_id]
        return {"total":len(routines),"by_status":dict(Counter(r["status"] for r in routines)),"due":len(self.due()),"recent_executions":history[:10],"completion_count":sum(r["completion_count"] for r in routines),"failure_count":sum(r["failure_count"] for r in routines),"max_streak":max((r["streak"] for r in routines),default=0),"health":self.health(),"execution_success":sum(e["status"]=="COMPLETED" for e in control),"execution_failure":sum(e["status"]=="FAILED" for e in control),"registry_registered":any(e.get("component_id")==self.subsystem_id for e in (self.database_foundation.registered_components() if self.database_foundation else []))}
    def _record(self,action:str,target:str,status:str)->None:
        try:
            if self.database_foundation and self.database_foundation.current_schema_version()>=self.database_foundation.expected_schema_version:self.database_foundation.executions.record(self.subsystem_id,action,target,status,actor="routine",result={"target_id":target,"version":"v1.8"})
        except Exception:
            return
