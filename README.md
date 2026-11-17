# Calorie Tracker
#### Video Demo: https://youtu.be/T4XQ9ewOMAM
#### Description:

## What it does
This is a terminal program that helps you track how many calories you eat in a day. You just type the name of the food and how many grams you are eating, and the program looks up the calories from the USDA food database and shows your total. Every meal you add or remove is saved to `meal.csv` so your list is still there the next time you run the program.

## Files
- `project.py` - The main file for the project. It has the `DailyLog` class that keeps track of your meals in a list, `main()` which runs the 6-option menu loop, `get_food()` and `validate_grams()` to get and check user input, `get_calories_per_100g()` and `find_calories()` to search the USDA API and pull out the kcal number, `get_total_calories()` to do the calorie math for your portion size, and `save_log()` and `load_log()` to write and read `meal.csv`.
- `test_project.py` - My test file for `pytest`. It tests `validate_grams`, `get_total_calories`, `find_calories`, and `save_log` / `load_log`. For `find_calories`, I pass in a fake dictionary that looks like the JSON from the USDA API, and for the CSV tests I use pytest's `tmp_path` so it doesn't mess with my real `meal.csv`. Because `find_calories` is separate from `get_calories_per_100g`, none of the tests actually call the API, so they run without internet or an API key.
- `requirements.txt` - The libraries you need to install: `requests` (to call the USDA API), `python-dotenv` (to load the API key from `key.env`), and `pytest` (to run the tests).
- `meal.csv` - Created by the program when you add or remove a meal. It stores your meals with three columns: `name`, `grams`, and `calories`.
- `key.env` - Not included in the project folder so I don't upload my private key. You need to make this file yourself and put one line in it: `USDA_API_KEY=your_key_here`.

## Design choices
1. **USDA FoodData Central vs Open Food Facts.** At first I looked at Open Food Facts, but it is mostly for packaged store foods with barcodes. When I tested searching for basic stuff I actually eat like rice and dal, Open Food Facts gave messy results from random brands, while USDA FoodData Central (filtering by `Foundation,SR Legacy,Survey (FNDDS)`) gave normal whole-food data for plain rice per 100g right at the top.

2. **Typing only the food and grams.** I could have made the user type the calories themselves, or pick serving sizes like "1 bowl" or "1 cup", but nobody's bowl is the same size and looking up calories yourself defeats the point of the app. Since the USDA gives calories per 100 grams, asking for the food name and the grams lets the program do the exact math (`grams * calories_per_100g / 100`) for you.

3. **Using a `DailyLog` class and calculating `total` from the list.** Instead of keeping a global list of meals and a separate `total_calories` variable that I add to or subtract from, I put the meal list inside a `DailyLog` class and made `total` a `@property` that adds up the calories from `self._meals` every time you ask for it. If I stored the total separately, it would be easy to forget to update it when removing a meal or loading a file, so calculating it straight from the list keeps it from ever getting out of sync.

4. **Removing a meal by its number instead of its name.** When you pick option 3 to remove a meal, the program shows the numbered list first and asks for the number instead of the food name. I did this because if you eat rice twice in the same day, typing `"rice"` wouldn't tell the program which one to delete, and it's also annoying if you make a typo spelling a long food name.

5. **Keeping the lookup, calorie math, and grams check as separate functions outside the class.** `DailyLog` only cares about holding meals in a list, so I kept `validate_grams`, `find_calories`, `get_calories_per_100g`, and `get_total_calories` as normal functions outside the class. This made testing way easier for CS50P because I can import those functions directly in `test_project.py` and test the math, bad inputs, and JSON parsing without having to fake `input()` prompts or make real internet requests.

6. **Putting the API key in `key.env` instead of in the code.** I could have just pasted my API key as a string at the top of `project.py`, which is simpler, but then anyone who sees my code on GitHub could take my key and use up my request limit. Putting it in `key.env` and reading it with `load_dotenv("key.env")` and `os.environ.get("USDA_API_KEY")` keeps my key out of `project.py`.

## How to run it
1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
2. Go to `https://fdc.nal.usda.gov/api-key-signup.html` and sign up for a free USDA API key.
3. Make a file called `key.env` in the same folder as `project.py` and paste your key inside like this:
   ```env
   USDA_API_KEY=your_api_key_here
   ```
4. Run the program:
   ```bash
   python project.py
   ```
5. To run the tests:
   ```bash
   pytest
   ```

## Limits and future ideas
Right now the program has a few limits. Because `load_log()` loads everything from `meal.csv` every time you start the program, meals from yesterday are still in there unless you remove them yourself or delete `meal.csv`, so it isn't strictly locked to one calendar day yet. Also, raw and cooked weights have very different calories (100g of raw rice is way more calories than 100g of cooked rice because of the water), and since the program grabs the first search result from the USDA, typing just `"rice"` instead of `"rice cooked"` might not match what's on your plate. Some local or homemade dishes also aren't in the USDA database at all.

If I keep working on this, the next things I would add are a date column in `meal.csv` so it only counts today's meals toward your daily total, a way to pick from the top 5 search results so you can choose between raw and cooked, and a daily calorie goal so it tells you how many calories you have left.