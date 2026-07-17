from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class SQLiteConnectionLayer:
    """Creates configured SQLite connections and owns transaction boundaries."""

    def __init__(self, database_path: Path, *, timeout: float = 30.0) -> None:
        self.database_path = Path(database_path)
        self.timeout = timeout

    def connect(self, *, read_only: bool = False) -> sqlite3.Connection:
        if read_only:
            if not self.database_path.is_file():
                raise FileNotFoundError(self.database_path)
            target = self.database_path.resolve().as_uri() + "?mode=ro"
            connection = sqlite3.connect(target, timeout=self.timeout, uri=True)
        else:
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
            connection = sqlite3.connect(self.database_path, timeout=self.timeout)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        if not read_only:
            connection.execute("PRAGMA journal_mode = WAL")
        return connection

    @contextmanager
    def connection(self, *, read_only: bool = False) -> Iterator[sqlite3.Connection]:
        connection = self.connect(read_only=read_only)
        try:
            yield connection
        finally:
            connection.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
