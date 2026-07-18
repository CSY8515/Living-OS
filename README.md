# Living OS v2.0.3

> Living OS v2.0.3 reworks Home as a minimal Today-focused Living OS Core surrounded by six existing life-system launch points while preserving every feature, route, subsystem, and data contract.

The v2.0.3 release keeps the premium dark glass interface while removing dashboard and management surfaces from Home in favor of a spacious Personal Operating System entry experience.

Living OS is the Module layer in the official Skeleton Architecture:

Living OS (Module) → Subsystem → Engine → Function

v1.2 is an architecture migration, not a feature release. All runtime implementation now lives under subsystems/ in Foundation, Operations, Insight, Experience, or Compatibility. Existing app.*, core.*, modules.*, and shared.* paths remain exact module aliases, preserving imports and monkeypatch behavior.

## Run

    python -m pip install -r requirements.txt
    python -m streamlit run app.py

## Verify

    python -m compileall -q app.py app core modules shared subsystems tests
    python -m unittest discover -s tests -v

Existing data paths and structures, backups, explicit migration approval, and AI non-write guarantees are preserved. See ARCHITECTURE.md, STRUCTURE.md, VERSION.md, RELEASE_NOTES_v1.2.md, and docs/v1.2/.

## Finance Subsystem v1.0

Finance is the first official production-grade reference Subsystem. Use only its public facade:

    from pathlib import Path
    from subsystems.finance import FinanceSubsystem

    finance = FinanceSubsystem(Path.cwd())
    finance.record_income(3000000, "Salary", "2026-07-01")
    status = finance.summary_report("2026-07")

It provides Ledger, Budget, Cash Flow, Savings, Report, and explicit legacy Migration behavior. See docs/finance-subsystem-v1.0/ and RELEASE_NOTES_FINANCE_SUBSYSTEM_v1.0.md.

## Health Subsystem v1.0

Health is available only through its Living OS facade:

    from pathlib import Path
    from subsystems.health import HealthSubsystem

    health = HealthSubsystem(Path.cwd())
    health.record_weight(70.0, "2026-07-15")
    report = health.monthly_report("2026-07")

Health data is sensitive and ignored by Git. Reads do not create storage, and real migration requires explicit approval. See `docs/health-subsystem-v1.0/` and `RELEASE_NOTES_v1.3.md`.

## Housing Subsystem v1.0

Housing is available through its public facade:

    from pathlib import Path
    from subsystems.housing import HousingSubsystem

    housing = HousingSubsystem(Path.cwd())
    housing.create_candidate(
        name="Candidate A", deposit=10000000, monthly_rent=600000,
        maintenance_fee=100000, maintenance_fee_provided=True,
        commute_minutes=30, parking_available=True,
    )
    report = housing.housing_report()

Housing preserves the legacy scoring formula while adding isolated CRUD, comparison, reports, and explicit dry-run-first migration. Reads do not create storage, legacy Housing files remain unchanged, and no real migration is included in the v1.4 release. See `docs/housing-subsystem-v1.0/` and `RELEASE_NOTES_v1.4.md`.

## Vehicle Subsystem v1.0

Vehicle is available through its public facade:

    from pathlib import Path
    from subsystems.vehicle import VehicleSubsystem

    vehicle = VehicleSubsystem(Path.cwd())
    car = vehicle.create_vehicle("Daily Car", "Maker", "Model", 2024, "hybrid")
    vehicle.record_odometer(car["vehicle_id"], 12000, "2026-07-16")

Vehicle provides profiles, kilometer odometer history, maintenance records and schedules, fuel/charging costs, and deterministic status reports. Sensitive storage is isolated and lazy; reads do not create it. No legacy Vehicle migration exists. See `docs/vehicle-subsystem-v1.0/` and `RELEASE_NOTES_v1.5.md`.

## Food Subsystem v1.0

Food is available through its public facade:

    from pathlib import Path
    from subsystems.food import FoodSubsystem

    food = FoodSubsystem(Path.cwd())
    rice = food.create_ingredient(
        "Rice", "grain", 100, "g",
        {"calories": 130, "protein": 2.7, "carbohydrate": 28, "fat": 0.3},
    )

Food provides ingredients, recipes, cooking and meal records, owner-entered nutrition arithmetic, and deterministic reports. Sensitive storage is isolated and lazy; reads do not create it. Food does not access Health or Finance and performs no unit conversion or nutrition estimation. See `docs/food-subsystem-v1.0/` and `docs/roadmap/Living_OS_v1.6_SCOPE.md`.

## Production deployment

Production URL: [https://living-os-h5uinmvmjpvv6m8phat28a.streamlit.app/](https://living-os-h5uinmvmjpvv6m8phat28a.streamlit.app/)

Streamlit Community Cloud coordinates:

- Repository: `CSY8515/Living-OS`
- Branch: `main`
- Entrypoint: `app.py`
- Python: 3.12 recommended
- Secrets: none required

The current file-backed stores are intended for a single-owner runtime. A hosted local filesystem is not durable Finance, Food, Health, Housing, Vehicle, Knowledge, Routine, Investment, Job, Personal Growth, or Collaboration storage.
