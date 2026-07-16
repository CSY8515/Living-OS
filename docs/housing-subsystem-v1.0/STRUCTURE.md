# Housing Subsystem v1.0 Structure

    subsystems/housing/
      __init__.py
      subsystem.py
      engines/
        __init__.py
        candidate.py
        comparison.py
        migration.py
        report.py
        scoring.py
        storage.py
        validation.py

`subsystem.py` is the composition root and `HousingSubsystem` is the only supported public object. The default runtime database is `data/housing/housing.sqlite3`; callers may inject another path for testing, replacement, or rollback.

Living OS integration is limited to the v1.4 catalog, Experience page and shell, tests, ignored runtime path, and synchronized documentation.
