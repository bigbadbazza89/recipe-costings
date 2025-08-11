import json
import os
import difflib

INGREDIENTS_FILE = "ingredients.json"
RECIPES_FILE = "recipes.json"

# 🧼 Input Validation Helpers
def get_positive_float(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value > 0:
                return value
            print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_non_empty_string(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Input cannot be empty.")

# 🔍 Fuzzy Matching Helper
def suggest_name(input_name, valid_names):
    input_name_lower = input_name.lower()
    for name in valid_names:
        if name.lower() == input_name_lower:
            return name  # Exact match, no prompt

    # Basic fuzzy suggestion: startswith or contains
    suggestions = [name for name in valid_names if input_name_lower in name.lower() or name.lower().startswith(input_name_lower)]
    if suggestions:
        suggestion = suggestions[0]
        confirm = input(f"Did you mean '{suggestion}' instead of '{input_name}'? (y/n): ").strip().lower()
        return suggestion if confirm == 'y' else input_name

    return input_name

# 🧱 Ingredient Class
class Ingredient:
    def __init__(self, name, weight_g, cost_per_g):
        self.name = name
        self.weight_g = weight_g
        self.cost_per_g = cost_per_g

    def total_cost(self):
        return self.weight_g * self.cost_per_g

# 🧱 Recipe Class
class Recipe:
    def __init__(self, name, portions):
        self.name = name
        self.portions = portions
        self.ingredients = []

    def add_ingredient(self, ingredient):
        self.ingredients.append(ingredient)

    def total_cost(self):
        return sum(ing.total_cost() for ing in self.ingredients)

    def cost_per_portion(self):
        return self.total_cost() / self.portions

# 🧠 Recipe Manager
class RecipeManager:
    def __init__(self):
        self.ingredients_db = self.load_data(INGREDIENTS_FILE)
        self.recipes_db = self.load_data(RECIPES_FILE)

    def load_data(self, filename):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                return json.load(f)
        return {}

    def save_data(self, filename, data):
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    def get_cost_per_gram(self, name):
        name = suggest_name(name, self.ingredients_db.keys())
        if name in self.ingredients_db:
            return self.ingredients_db[name]
        cost = get_positive_float(f"Enter cost per gram for {name}: ")
        self.ingredients_db[name] = cost
        self.save_data(INGREDIENTS_FILE, self.ingredients_db)
        return cost

    def create_recipe(self):
        name = get_non_empty_string("Enter recipe name: ")
        portions = int(get_positive_float("Enter number of portions: "))
        recipe = Recipe(name, portions)

        while True:
            ing_name = get_non_empty_string("Enter ingredient name: ")
            ing_name = suggest_name(ing_name, self.ingredients_db.keys())
            weight = get_positive_float(f"Enter weight in grams for {ing_name}: ")
            cost_per_g = self.get_cost_per_gram(ing_name)
            ingredient = Ingredient(ing_name, weight, cost_per_g)
            recipe.add_ingredient(ingredient)

            cont = input("Add another ingredient? (y/n): ").lower()
            if cont != 'y':
                break

        cost = recipe.cost_per_portion()
        print(f"\n✅ Cost per portion for '{name}': ${cost:.2f}")
        self.recipes_db[name] = round(cost, 2)
        self.save_data(RECIPES_FILE, self.recipes_db)

    def view_recipe_cost(self):
        if not self.recipes_db:
            print("📭 No recipes stored yet.")
            return

        print("\n📚 Stored Recipe Costings:")
        for name, cost in self.recipes_db.items():
            print(f" - {name}: ${cost:.2f}")

# 🚀 Main Program
def main():
    manager = RecipeManager()
    action = input("View recipe cost or create new recipe? (view/create): ").lower()
    if action == "view":
        manager.view_recipe_cost()
    elif action == "create":
        manager.create_recipe()
    else:
        print("Invalid option.")

if __name__ == "__main__":
    main()

