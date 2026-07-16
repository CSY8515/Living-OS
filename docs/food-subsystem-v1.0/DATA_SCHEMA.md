# Food Subsystem v1.0 Data Schema

Schema version: 1. Default sensitive store: `data/food/food.sqlite3`.

- `food_ingredients`: identity, name, category, base quantity/unit, optional calories/protein/carbohydrate/fat, archive status, timestamps.
- `food_recipes`: identity, name, positive servings, ordered instructions JSON, archive status, timestamps.
- `food_recipe_ingredients`: recipe and ingredient foreign keys, stable line order, positive quantity, explicit unit.
- `food_cooking_records`: identity, recipe foreign key, cooking date, servings produced, note, timestamp.
- `food_meals`: identity, meal date/type, optional recipe and cooking references, servings consumed, optional explicit nutrition override, note, timestamp.
- `food_meta`: schema and subsystem versions. No migration ledger exists.

Quantities and nutrition values persist as bounded decimal strings with at most three decimal places. Supported units are `g`, `kg`, `ml`, `l`, `item`, and `serving`. No conversion occurs. Recipe nutrition is complete only when every line unit matches its ingredient base unit and every nutrient is present.

Foreign keys are enabled. Writes are transactional. Reads do not create storage.
