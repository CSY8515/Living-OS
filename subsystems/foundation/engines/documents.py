from __future__ import annotations

import hashlib
import mimetypes
import os
from contextlib import closing
from pathlib import Path
from uuid import uuid4

from subsystems.foundation.engines.audit import append_audit
from subsystems.foundation.engines.contracts import CommandEnvelope, DocumentRef, DomainEvent, RecordRef
from subsystems.foundation.engines.storage import HubStore
from subsystems.foundation.engines.time import utc_now_iso


class DocumentService:
    def __init__(self, store: HubStore, content_root: Path) -> None:
        self.store = store
        self.content_root = content_root

    def add(
        self,
        filename: str,
        content: bytes,
        *,
        media_type: str | None = None,
        privacy_class: str = "personal",
    ) -> DocumentRef:
        clean_name = Path(filename).name.strip()
        if not clean_name:
            raise ValueError("Document filename is required.")
        if privacy_class not in {"public", "personal", "sensitive", "restricted"}:
            raise ValueError("Unknown document privacy class.")
        digest = hashlib.sha256(content).hexdigest()
        suffix = Path(clean_name).suffix.lower()
        relative = Path(digest[:2]) / f"{digest}{suffix}"
        target = self.content_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        created_content = False
        if not target.exists():
            temporary = target.with_suffix(target.suffix + f".{uuid4()}.tmp")
            try:
                with temporary.open("wb") as stream:
                    stream.write(content)
                    stream.flush()
                    os.fsync(stream.fileno())
                temporary.replace(target)
                created_content = True
            except OSError:
                temporary.unlink(missing_ok=True)
                raise

        document_id = str(uuid4())
        selected_media = media_type or mimetypes.guess_type(clean_name)[0] or "application/octet-stream"
        now = utc_now_iso()
        command = CommandEnvelope(
            "documents",
            "add",
            {"filename": clean_name, "privacy_class": privacy_class, "size_bytes": len(content)},
            reason="add-document",
        )
        self.store.initialize()
        try:
            with self.store.transaction() as connection:
                connection.execute(
                """
                INSERT INTO documents (
                    document_id, version, content_hash, filename, media_type, size_bytes,
                    privacy_class, storage_path, created_at
                ) VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    digest,
                    clean_name,
                    selected_media,
                    len(content),
                    privacy_class,
                    relative.as_posix(),
                    now,
                ),
            )
                self.store.append_event(
                    DomainEvent(
                        "documents",
                        "DocumentAdded",
                        RecordRef("documents", "document", document_id),
                        {"version": 1, "content_hash": digest},
                    ),
                    connection,
                )
                append_audit(connection, command, "accepted", {"document_id": document_id})
        except Exception:
            if created_content:
                target.unlink(missing_ok=True)
            raise
        return DocumentRef(
            document_id,
            digest,
            clean_name,
            selected_media,
            len(content),
            1,
            privacy_class,
        )

    def list(self) -> list[DocumentRef]:
        self.store.initialize()
        with closing(self.store.connect()) as connection:
            rows = connection.execute(
                """SELECT document_id, content_hash, filename, media_type, size_bytes,
                          version, privacy_class
                   FROM documents ORDER BY created_at DESC"""
            ).fetchall()
        return [DocumentRef(**dict(row)) for row in rows]

    def read(self, document_id: str, version: int = 1) -> bytes:
        self.store.initialize()
        with closing(self.store.connect()) as connection:
            row = connection.execute(
                "SELECT storage_path, content_hash FROM documents WHERE document_id=? AND version=?",
                (document_id, version),
            ).fetchone()
        if row is None:
            raise FileNotFoundError("Document is not registered.")
        content = (self.content_root / str(row["storage_path"])).read_bytes()
        if hashlib.sha256(content).hexdigest() != str(row["content_hash"]):
            raise OSError("Document integrity check failed.")
        return content
