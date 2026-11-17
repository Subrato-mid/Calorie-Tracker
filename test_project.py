import pytest

from project import (
    DailyLog,
    find_calories,
    get_total_calories,
    load_log,
    save_log,
    validate_grams,
)


def test_validate_grams():
    assert validate_grams("200") == 200.0
    assert validate_grams("0.5") == 0.5
    with pytest.raises(ValueError):
        validate_grams("abc")
    with pytest.raises(ValueError):
        validate_grams("0")
    with pytest.raises(ValueError):
        validate_grams("-5")


def test_get_total_calories():
    assert get_total_calories(200, 130) == 260
    assert get_total_calories(150, 0) == 0
    assert get_total_calories(144, 139) == 200.2
    with pytest.raises(ValueError):
        get_total_calories(0, 100)
    with pytest.raises(ValueError):
        get_total_calories(100, -1)


def test_find_calories():
    fake = {
        "foods": [
            {
                "foodNutrients": [
                    {"nutrientName": "Protein", "unitName": "G", "value": 3},
                    {"nutrientName": "Energy", "unitName": "KJ", "value": 540},
                    {"nutrientName": "Energy", "unitName": "KCAL", "value": 130},
                ]
            }
        ]
    }
    assert find_calories(fake) == 130
    with pytest.raises(ValueError):
        find_calories({"foods": []})
    with pytest.raises(ValueError):
        find_calories({"foods": [{"foodNutrients": []}]})


def test_save_log_and_load_log(tmp_path):
    file = tmp_path / "meals.csv"
    log = DailyLog()
    log.add_meal("rice", 200, 260)
    log.add_meal("dal", 150, 180.5)
    save_log(log, file)

    loaded = load_log(file)
    assert loaded.meals == log.meals
    assert loaded.total == 440.5

    assert load_log(tmp_path / "missing.csv").meals == []