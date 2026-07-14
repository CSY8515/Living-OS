from __future__ import annotations

from core.audit import append_audit
from core.contracts import CommandEnvelope, RecordRef, Relationship
from core.storage import HubStore


class RelationshipService:
    def __init__(self, store: HubStore) -> None:
        self.store = store

    def link(
        self,
        source: RecordRef,
        relation_type: str,
        target: RecordRef,
        *,
        actor: str = "owner",
    ) -> Relationship:
        if not relation_type.strip():
            raise ValueError("Relationship type is required.")
        relationship = Relationship(source, relation_type.strip(), target, actor)
        command = CommandEnvelope(
            "relationships",
            "link",
            {
                "source": f"{source.module_id}:{source.entity_type}:{source.record_id}",
                "relation_type": relationship.relation_type,
                "target": f"{target.module_id}:{target.entity_type}:{target.record_id}",
            },
            actor=actor,
            reason="link-canonical-records",
        )
        self.store.initialize()
        with self.store.transaction() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO relationships (
                    relationship_id, source_module, source_type, source_id, relation_type,
                    target_module, target_type, target_id, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    relationship.relationship_id,
                    source.module_id,
                    source.entity_type,
                    source.record_id,
                    relationship.relation_type,
                    target.module_id,
                    target.entity_type,
                    target.record_id,
                    actor,
                    relationship.created_at,
                ),
            )
            append_audit(
                connection,
                command,
                "accepted",
                {"relationship_id": relationship.relationship_id},
            )
        return relationship
