# Health Subsystem v1.0 Structure

    subsystems/health/
      __init__.py                 public HealthSubsystem export
      subsystem.py                Living OS interface and composition root
      engines/
        storage.py                lazy transactional SQLite schema and health
        validation.py             Health boundary validation
        weight.py                 weight CRUD, baseline, change
        body_composition.py       InBody measurements and timeline
        health_checkup.py         assessment, follow-up, metric comparison
        sleep.py                  bedtime, wake time, duration, fatigue
        exercise.py               activity records and statistics
        nutrition.py              meals, notes, Health goal linkage
        trend.py                  weight, InBody, sleep, exercise trends
        goal.py                   target weight/body fat and progress
        report.py                 daily, weekly, monthly Health reports
        migration.py              explicit JSON dry run and adoption

Default private state is `data/health/health.sqlite3`; an alternate database path is injectable. Only `HealthSubsystem` is public.

