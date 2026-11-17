import csv
import os

import requests
from dotenv import load_dotenv

load_dotenv("key.env")

API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
FILENAME = "meal.csv"


class DailyLog:
    def __init__(self):
        self._meals = []

    def add_meal(self, name, grams, calories):
        if grams <= 0 or calories < 0:
            raise ValueError("Invalid amount")
        self._meals.append({"name": name, "grams": grams, "calories": calories})

    def remove_meal(self, index):
        if index < 1 or index > len(self._meals):
            raise ValueError("Invalid index")
        self._meals.pop(index - 1)

    @property
    def total(self):
        return round(sum(meal["calories"] for meal in self._meals), 1)

    @property
    def meals(self):
        return list(self._meals)

    def summary(self):
        if not self._meals:
            return "No meals logged"
        lines = []
        for i, meal in enumerate(self._meals, start=1):
            lines.append(
                f"{i}. {meal['name']}, {meal['grams']}g, {meal['calories']} calories"
            )
        lines.append(f"Total: {self.total} calories")
        return "\n".join(lines)


def main():
    log = load_log()
    while True:
        print("Press a button to choose:")
        print(" 1. Check calories")
        print(" 2. Add meal")
        print(" 3. Remove meal")
        print(" 4. View total calories for the day")
        print(" 5. Get summary")
        print(" 6. Quit")

        try:
            choice = int(input("Choice: "))
        except ValueError:
            print("Please type a number")
            continue

        match choice:
            case 1:
                try:
                    name, grams = get_food()
                    per_100g = get_calories_per_100g(name)
                    print(f"{get_total_calories(grams, per_100g)} calories")
                except ValueError as e:
                    print(e)
                except requests.RequestException:
                    print("Could not reach the food database. Try again.")
            case 2:
                try:
                    name, grams = get_food()
                    per_100g = get_calories_per_100g(name)
                    total = get_total_calories(grams, per_100g)
                    log.add_meal(name, grams, total)
                    save_log(log)
                    print(f"Added {name}: {total} calories")
                except ValueError as e:
                    print(e)
                except requests.RequestException:
                    print("Could not reach the food database. Try again.")
            case 3:
                print(log.summary())
                try:
                    index = int(input("Meal number to remove: "))
                    log.remove_meal(index)
                    save_log(log)
                except ValueError:
                    print("Invalid meal number")
            case 4:
                print(f"Total calories you ate today is: {log.total}")
            case 5:
                print(log.summary())
            case 6:
                print("Thanks for using my app")
                break
            case _:
                print("Invalid input")


def validate_grams(text):
    grams = float(text)  # raises ValueError for text like "abc"
    if grams <= 0:
        raise ValueError("Grams must be above 0")
    return grams


def get_food():
    name = input("What are you eating? ").strip()
    while not name:
        name = input("Please type a food name: ").strip()
    while True:
        try:
            return name, validate_grams(input("How many grams? "))
        except ValueError:
            print("Please enter a number above 0")


def find_calories(data):
    foods = data.get("foods", [])
    if not foods:
        raise ValueError("Food not found")
    for nutrient in foods[0]["foodNutrients"]:
        if nutrient["nutrientName"] == "Energy" and nutrient["unitName"] == "KCAL":
            return nutrient["value"]
    raise ValueError("No calorie data for this food")


def get_calories_per_100g(food):
    key = os.environ.get("USDA_API_KEY")
    if key is None:
        raise RuntimeError("USDA_API_KEY is not set")
    response = requests.get(
        API_URL,
        params={
            "api_key": key,
            "query": food,
            "dataType": "Foundation,SR Legacy,Survey (FNDDS)",
            "pageSize": 1,
        },
        timeout=10,
    )
    response.raise_for_status()
    return find_calories(response.json())


def get_total_calories(grams, calories_per_100g):
    if grams <= 0 or calories_per_100g < 0:
        raise ValueError("Invalid amount")
    return round(grams * calories_per_100g / 100, 1)


def save_log(log, filename=FILENAME):
    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "grams", "calories"])
        writer.writeheader()
        for meal in log.meals:
            writer.writerow(meal)


def load_log(filename=FILENAME):
    log = DailyLog()
    try:
        with open(filename, newline="") as file:
            for row in csv.DictReader(file):
                log.add_meal(row["name"], float(row["grams"]), float(row["calories"]))
    except FileNotFoundError:
        pass
    return log


if __name__ == "__main__":
    main()