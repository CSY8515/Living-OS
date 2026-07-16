# Living OS v1.6 Scope

Status: **RELEASED AND PRODUCTION-VERIFIED**

Planning date: 2026-07-16

Baseline: Living OS v1.5 Stable, commit `a4e6b68`

Baseline verification: Python compilation passed and the complete 81-test suite passed.

The owner approved this exact scope on 2026-07-16. Implementation and development verification are complete. This approval did not authorize migration, commit, release, or deployment, and none was performed.

## Scope decision

Living OS v1.6 proposes **Food Subsystem v1.0** as a new independently replaceable sensitive-data subsystem. Food is the next unimplemented domain explicitly present in `config/module_registry.json`; Finance, Health, Housing, and Vehicle are already implemented. Food will follow the same facade, private-engine, isolated-storage, deterministic-reporting, and no-write-on-read rules established by the v1.5 Stable architecture.

Food Subsystem v1.0 is limited to ingredients, recipes, cooking records, meal records, explicit nutrition values, and deterministic Food reports. It will not integrate with Health, Finance, Inventory, external services, AI, reminders, or automation.

## 1. Objectives

1. Add one supported public `FoodSubsystem` facade with all implementation engines kept private.
2. Maintain an ingredient catalog with explicit measurement units and optional nutrition values.
3. Maintain recipes with serving counts, ordered instructions, and ingredient quantities.
4. Record cooking and meal history without automatically modifying any other Living OS subsystem.
5. Produce deterministic, attributable Food summaries from stored records without AI or external data.
6. Keep Food data isolated, lazy, transactional, injectable for tests, and excluded from Git.
7. Add Food through a new v1.6 manifest and one Food page while leaving all v1.5 and older manifests unchanged.
8. Preserve every v1.5 import, page, behavior, data path, schema, migration rule, privacy boundary, and safety contract.

## 2. Features to be implemented

### Public boundary

The only supported external import will be:

```python
from subsystems.food import FoodSubsystem
```

`FoodSubsystem` will be the composition root and the only supported Living OS interface. Food engines will not be imported directly by Experience or by another subsystem.

### Private engines and responsibilities

| Private engine | Responsibility |
|---|---|
| Ingredient | Create, read, list, update, and archive ingredients; store one explicit base quantity/unit and optional nutrition values |
| Recipe | Create, read, list, update, and archive recipes; maintain servings, ordered instructions, and ingredient lines |
| Cooking | Record and list completed cooking sessions for a recipe, including date, servings produced, and notes |
| Meal | Record and list meals, optionally linked to a recipe or cooking session, with meal type, servings consumed, and notes |
| Nutrition | Calculate recipe and meal nutrition only from owner-entered ingredient values and explicit quantities |
| Report | Produce deterministic date-bounded meal, cooking, recipe-frequency, and nutrition summaries with source counts |
| Storage | Provide lazy SQLite schema initialization, transactions, foreign-key enforcement, integrity health, and export snapshots |
| Validation | Validate identifiers, ISO dates, bounded text, enums, decimal quantities, serving counts, and non-negative nutrition values |

### Proposed facade operations

The public facade will be limited to:

- Lifecycle and diagnostics: `health()`, `interface_manifest()`, `export_snapshot()`, `database_path`.
- Ingredients: `create_ingredient()`, `get_ingredient()`, `list_ingredients()`, `update_ingredient()`, `archive_ingredient()`.
- Recipes: `create_recipe()`, `get_recipe()`, `list_recipes()`, `update_recipe()`, `archive_recipe()`, `set_recipe_ingredients()`.
- Cooking: `record_cooking()`, `list_cooking_records()`.
- Meals: `record_meal()`, `list_meals()`.
- Nutrition and reports: `recipe_nutrition()`, `meal_nutrition()`, `food_report()`.

Method arguments and return shapes must be documented before implementation and covered by tests. Reads, calculations, reports, health checks, exports against an absent store, application startup, and Food page load must not create storage.

### Data model

Add isolated `data/food/food.sqlite3`, created transactionally only by the first explicit Food write. Schema version is 1.

- `food_ingredients`: subsystem-generated ID; name; category; base quantity; unit; optional calories, protein, carbohydrate, and fat values for that base quantity; active/archive status; UTC timestamps.
- `food_recipes`: subsystem-generated ID; name; positive serving count; ordered instructions; active/archive status; UTC timestamps.
- `food_recipe_ingredients`: recipe foreign key; ingredient foreign key; positive quantity; unit; stable line order; unique recipe/line identity.
- `food_cooking_records`: subsystem-generated ID; recipe foreign key; ISO cooked date; positive servings produced; note; created timestamp.
- `food_meals`: subsystem-generated ID; ISO eaten date; meal type; optional recipe foreign key; optional cooking-record foreign key; positive servings consumed; optional explicit nutrition override; note; created timestamp.
- `food_meta`: schema and subsystem versions. No migration ledger.

Quantities and nutrition values will use bounded decimal string persistence rather than binary floating point. Public results may expose numeric decimal-compatible values following the project’s existing validation conventions. Units are owner-entered from a small validated set; v1.6 will not perform density, mass/volume, currency, or automatic serving conversions. Recipe nutrition is calculated only where ingredient units match their declared base units. Incomplete inputs must be reported as incomplete, never silently estimated.

### Food page and manifest

Add one Food page to canonical and compatibility-mode navigation. The page will support ingredient and recipe maintenance, explicit cooking and meal recording, and deterministic summaries. It must use only the public `FoodSubsystem` facade.

Add `V16_STABLE_MANIFESTS = V15_STABLE_MANIFESTS + (food manifest,)`. All older manifest tuples must remain unchanged. The proposed Food manifest is:

- Module ID: `food`
- Name: `Food Subsystem`
- Subsystem version: `1.0.0`
- Living OS compatibility: `>=1.6,<2.0`
- Privacy class: `sensitive`
- Capabilities: `ingredient-catalog`, `recipe`, `cooking-record`, `meal-record`, `nutrition-summary`, `food-report`

Visible version labels may change to `v1.6` only after implementation and complete verification pass. Stable/release wording is not authorized during development.

### Explicitly excluded

- Grocery lists, pantry stock, expiry tracking, purchasing, barcode scanning, or Inventory functionality.
- Meal planning calendars, reminders, notifications, schedulers, background jobs, or automation.
- Health goals, dietary prescriptions, medical advice, allergy safety guarantees, or direct Health data access.
- Finance posting, budgets, price histories, cost allocation, or direct Finance data access.
- AI meal suggestions, recipe generation, image recognition, autonomous writes, embeddings, or model calls.
- External nutrition databases, recipe sites, delivery services, retailers, devices, APIs, or web scraping.
- Attachments, photographs, OCR, CSV import, bulk import, or bulk export beyond the subsystem snapshot.
- Automatic unit conversion, density conversion, currency conversion, nutrition estimation, or serving inference.
- Legacy Food migration, compatibility aliases, or discovery of undeclared owner data.
- Changes to existing subsystem records, schemas, migrations, backups, requirements, authentication, hosted storage, or deployment configuration.
- Unrelated refactoring, feature additions, commit, push, tag, release, publication, or deployment.

## 3. Files expected to change

### Scope-design phase authorized by this request

Only this file:

- `docs/roadmap/Living_OS_v1.6_SCOPE.md` (new)

### Expected implementation files after separate approval

New runtime files:

```text
subsystems/food/__init__.py
subsystems/food/subsystem.py
subsystems/food/engines/__init__.py
subsystems/food/engines/ingredient.py
subsystems/food/engines/recipe.py
subsystems/food/engines/cooking.py
subsystems/food/engines/meal.py
subsystems/food/engines/nutrition.py
subsystems/food/engines/report.py
subsystems/food/engines/storage.py
subsystems/food/engines/validation.py
```

New tests and subsystem documentation:

```text
tests/test_food_subsystem_v10.py
docs/food-subsystem-v1.0/ARCHITECTURE_REVIEW.md
docs/food-subsystem-v1.0/DATA_SCHEMA.md
docs/food-subsystem-v1.0/ENGINE_MAP.md
docs/food-subsystem-v1.0/MIGRATION_ROLLBACK_PLAN.md
docs/food-subsystem-v1.0/TEST_REPORT.md
docs/food-subsystem-v1.0/REGRESSION_REPORT.md
```

Existing runtime and test files expected to receive minimal changes:

- `subsystems/operations/engines/catalog.py`: append the v1.6 Food manifest only.
- `subsystems/experience/engines/pages.py`: add the Food page only.
- `subsystems/experience/engines/shell.py`: compose/register Food, use the v1.6 manifest, add navigation, and update the development version label after verification.
- `tests/test_streamlit.py`: add Food storage to no-write fingerprints, add the Food page, and update the current development-version assertion.
- `tests/test_v10.py`: update current-version assertions only; preserve historical expectations.
- `tests/test_v12_architecture.py`: register Food as self-only and allow Experience to import only its public facade.
- `.gitignore`: add `data/food/`.

Documentation expected to be synchronized after implementation verification:

- `README.md`
- `MASTER_DESIGN.md`
- `ARCHITECTURE.md`
- `STRUCTURE.md`
- `ROADMAP.md`
- `VERSION.md`
- `CHANGELOG.md`
- `KNOWN_ISSUES.md`
- `docs/README.md`
- `config/modules/README.md`
- `docs/roadmap/Living_OS_v1.6_SCOPE.md` (status and verified results only)
- A v1.6 development report; release-readiness or release-note files only if separately requested later.

No change is expected for `app.py`, compatibility alias packages, Foundation, Operations engines other than the manifest catalog, Insight, existing domain subsystems, `config/module_registry.json`, tracked owner-data files, requirements, release metadata, or deployment configuration.

## 4. Architecture impact

The top-level architecture remains unchanged:

```text
Living OS (Module)
  -> Food Subsystem
       -> private Food Engines
            -> Functions and methods
```

Allowed dependency direction:

```text
Experience -> Food public facade
Food facade -> Food private engines
Food engine -> Food engine / Python standard library
```

Food must not import Foundation, Operations, Insight, Compatibility, Finance, Health, Housing, Vehicle, or any public compatibility path. No other domain subsystem may import Food. Experience may import `FoodSubsystem` only from `subsystems.food` and may not import Food engines.

Food will be a peer of Finance, Health, Housing, and Vehicle. It will not change the ownership or responsibilities of the five architectural subsystems. The executable catalog gains one append-only v1.6 manifest tuple; `V15_STABLE_MANIFESTS` and all older constants remain unchanged. `V2_STABLE_MANIFESTS` remains the existing compatibility alias.

The Health subsystem’s existing `nutrition_records` remain simple Health observations linked only to Health goals. Food nutrition data belongs solely to Food. v1.6 will not synchronize, migrate, join, duplicate, or automatically write between these stores.

## 5. Backward compatibility

- The verified baseline is Living OS v1.5 Stable at commit `a4e6b68`, with 81 tests passing.
- All v1.5 imports, exact module aliases, pages, behavior, schemas, data paths, and stored data remain unchanged.
- `V15_STABLE_MANIFESTS` and older manifests remain byte-for-byte behaviorally unchanged; Food exists only in `V16_STABLE_MANIFESTS`.
- Existing Finance, Health, Housing, Vehicle, Hub, settings, registry, report, backup, AI, security, and migration contracts remain unchanged.
- `config/module_registry.json` remains unchanged. Its `food_os` record is legacy planning evidence, not the executable v1.6 manifest.
- No existing nutrition record is reinterpreted as a Food record, and Food records are never presented as Health records.
- An absent Food database is valid. Reverting the code leaves all v1.5 data usable and any Food database dormant.
- No automatic migration will run during startup, reads, reports, page rendering, tests, release, or deployment.

### Migration and rollback

There is no legacy Food implementation or declared Food owner-data source in the repository. v1.6 must not scan for, infer, or import one. No migration engine or migration ledger is included.

Schema version 1 initialization occurs only on the first explicit Food write. Code rollback returns to the v1.5 implementation. `data/food/food.sqlite3` may remain dormant and must never be deleted automatically. Any future data migration, removal, or restoration requires separate approval and a verified backup limited to Food data.

## 6. Test plan

All tests must use temporary or injected storage and must never write to repository owner data.

Add seven focused Food tests:

1. Public export, exact manifest, injectable independent storage, and read-without-create behavior.
2. Ingredient lifecycle, validation, filtering, archive behavior, and decimal persistence.
3. Recipe lifecycle, ordered instructions, ingredient-line replacement, unit validation, and transaction rollback.
4. Cooking records and meal records, optional linkage rules, date filtering, and invalid-reference rejection.
5. Deterministic recipe/meal nutrition calculations, incomplete-input disclosure, and absence of estimation or implicit conversion.
6. Food reports, export snapshot, SQLite integrity, foreign-key enforcement, health diagnostics, and transactional failure behavior.
7. Privacy ignore rule, manifest separation, subsystem import boundaries, and prohibition on Health/Finance/other-domain coupling.

Regression verification must include:

- Python compilation/import checks across `app.py`, `app`, `core`, `modules`, `shared`, `subsystems`, and `tests`.
- The complete existing 81-test regression suite plus all new Food tests; planned total: 88 passing tests.
- All canonical and compatibility-mode pages rendering without exceptions.
- Fingerprint verification that startup and every page load leave all tracked and private stores unchanged.
- Architecture tests proving Food’s self-only imports and Experience’s facade-only access.
- SQLite `integrity_check`, foreign-key checks, transaction rollback, and lazy initialization checks.
- Exact comparison proving all v1.5 and older manifest tuples remain unchanged.
- Diff review proving no owner data, generated database, dependency, unrelated source, release, or deployment changes.

If implementation requires a behavior or file outside this plan, development must stop and request a scope amendment rather than silently expanding the release.

## 7. Acceptance criteria

Implementation may be reported complete only when all of the following are true:

- Exactly the included Food facade, engines, page, and v1.6 manifest are implemented; excluded features remain absent.
- The only supported external Food interface is `FoodSubsystem`.
- Food reads, reports, health checks, exports against an absent store, startup, and page load do not create or mutate storage.
- Explicit writes are validated and transactional; foreign keys and integrity checks pass.
- Nutrition calculations use only explicit owner-entered values, disclose incomplete data, and never estimate or convert implicitly.
- Food does not import or mutate Health, Finance, Housing, Vehicle, Compatibility, or another domain.
- All 81 baseline tests and the seven planned Food tests pass, for 88/88 total unless an approved test-count amendment documents a justified change.
- Compilation, architecture enforcement, every-page smoke checks, no-write fingerprints, and headless Streamlit startup pass.
- All v1.5 functionality, public imports, data contracts, paths, manifests, and safety guarantees remain compatible.
- Documentation accurately matches the implemented behavior and final verification results.
- The final diff contains only approved implementation, tests, and documentation; it contains no owner data or generated runtime artifacts.
- No migration, commit, push, tag, release, publication, or deployment is performed as part of development.

## 8. Risks

| Risk | Control |
|---|---|
| Food nutrition overlaps the existing Health nutrition log | Keep databases, facades, schemas, pages, and reports independent; prohibit cross-domain imports and synchronization |
| Nutrition values may be mistaken for medical guidance | Label values as owner-entered records, provide deterministic arithmetic only, and exclude recommendations or health claims |
| Unit mismatches could produce false totals | Use a small validated unit set, calculate only matching units, disclose incomplete results, and prohibit implicit conversion |
| Recipe ingredient replacement could leave partial state | Validate the entire replacement first and execute it in one transaction |
| Archived ingredients or recipes could invalidate history | Preserve referenced records and historical links; archive instead of destructive cascade deletion |
| Page rendering could create sensitive storage | Retain lazy reads and extend page-load fingerprint tests to `data/food/food.sqlite3` |
| Scope could drift into Inventory, Health, Finance, Calendar, or AI | Enforce the explicit exclusions, architecture test matrix, expected-file list, and scope-amendment stop rule |
| Streamlit Community Cloud storage is ephemeral | Document Food storage as single-owner local state and do not claim hosted durability |
| Existing v1.5 behavior could regress during shell integration | Append manifests, make minimal page wiring changes, and run the complete regression and no-write suites |

## 9. Development checklist

### Approval gate

- [x] Owner approves this exact v1.6 scope.
- [x] No scope amendment was required before source changes.
- [ ] Implementation, migration, release, and deployment remain unapproved until separately authorized.

### Baseline and design

- [x] Reconfirm a clean v1.5 Stable baseline and 81 passing tests immediately before implementation.
- [x] Reconfirm no undeclared Food implementation or owner-data source exists.
- [x] Freeze public method signatures, return shapes, schema, validated units, and nutrition calculation rules in subsystem documentation.
- [x] Confirm the complete implementation diff is limited to the approved file inventory.

### Implementation

- [x] Add lazy transactional Food storage and validation.
- [x] Add Ingredient, Recipe, Cooking, Meal, Nutrition, and Report engines.
- [x] Add the `FoodSubsystem` facade and export only that facade publicly.
- [x] Append `V16_STABLE_MANIFESTS` without altering older manifests.
- [x] Add the Food page and minimal shell composition/navigation.
- [x] Add `data/food/` to privacy exclusions without adding generated data.
- [x] Avoid unrelated refactoring and preserve all existing domain boundaries.

### Verification

- [x] Add and pass the seven focused Food tests.
- [x] Pass Python compilation/import checks.
- [x] Pass the complete planned 88-test regression suite.
- [x] Pass architecture and facade-only dependency checks.
- [x] Pass SQLite integrity, foreign-key, transaction rollback, and lazy-storage checks.
- [x] Render every canonical and compatibility page without errors or writes.
- [x] Verify headless Streamlit startup.
- [x] Verify all v1.5 and older manifests, imports, schemas, paths, and owner data remain unchanged.
- [x] Inspect the complete diff for scope, secrets, caches, private data, generated databases, and unrelated changes.

### Documentation and stop condition

- [x] Synchronize governing and subsystem documentation with verified implementation results.
- [x] Produce the final v1.6 development report with changed files, test evidence, compatibility results, limitations, and remaining approvals.
- [ ] Stop after implementation, testing, and the development report.
- [ ] Do not migrate owner data, commit, push, tag, release, publish, or deploy without separate explicit approval.

## Approval

**COMPLETE.** Implementation, verification, official commit, GitHub Release, Streamlit deployment, and production verification are complete. Migration remains excluded and was not performed.
