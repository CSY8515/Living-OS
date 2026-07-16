# Food Subsystem v1.0 Engine Map

| Engine | Public facade functions |
|---|---|
| Ingredient | `create_ingredient`, `get_ingredient`, `list_ingredients`, `update_ingredient`, `archive_ingredient` |
| Recipe | `create_recipe`, `get_recipe`, `list_recipes`, `update_recipe`, `archive_recipe`, `set_recipe_ingredients` |
| Cooking | `record_cooking`, `list_cooking_records` |
| Meal | `record_meal`, `list_meals` |
| Nutrition | `recipe_nutrition`, `meal_nutrition` |
| Report | `food_report` |
| Storage/interface | `health`, `interface_manifest`, `export_snapshot`, `database_path` |

`FoodSubsystem` is the only supported external object. Experience imports the facade only; no external subsystem imports Food engines.

## Public method contract

- `create_ingredient(name, category, base_quantity, unit, nutrition=None)` returns one ingredient record. `nutrition` accepts only `calories`, `protein`, `carbohydrate`, and `fat`.
- `get_ingredient(ingredient_id)` returns one record or raises `KeyError`. `list_ingredients(status=None, category=None)` returns ordered records. `update_ingredient(ingredient_id, **changes)` accepts only documented ingredient fields; `archive_ingredient(ingredient_id)` returns the archived record.
- `create_recipe(name, servings, instructions=())` returns one recipe. `get_recipe(recipe_id)` also returns ordered ingredient lines. `list_recipes(status=None)`, `update_recipe(recipe_id, **changes)`, and `archive_recipe(recipe_id)` follow the same lifecycle contract.
- `set_recipe_ingredients(recipe_id, ingredients)` transactionally replaces all lines. Each line contains only `ingredient_id`, positive `quantity`, and `unit`; the return value is the resulting ordered line list.
- `record_cooking(recipe_id, cooked_on, servings_produced, note="")` returns one cooking record. `list_cooking_records(start_on=None, end_on=None, recipe_id=None)` returns date-ordered records.
- `record_meal(eaten_on, meal_type, servings_consumed, recipe_id=None, cooking_id=None, nutrition_override=None, note="")` returns one meal. A cooking link supplies its recipe and must agree with an explicit recipe. `list_meals(start_on=None, end_on=None, meal_type=None, recipe_id=None)` returns date-ordered records.
- `recipe_nutrition(recipe_id)` and `meal_nutrition(meal_id)` return `complete`, `owner_entered_only`, source/missing details, and exact decimal-string totals when complete. Incomplete results return no totals.
- `food_report(start_on=None, end_on=None)` returns counts, deterministic recipe frequency, nutrition source/completeness counts and totals, plus attributable meal and cooking records.
- `health()` and `interface_manifest()` return diagnostics/contracts without initializing storage. `export_snapshot()` returns all Food tables without initializing an absent store. `database_path` returns the injected/default path.
