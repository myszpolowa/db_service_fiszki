# seeders/seed_data.py - Contains all seed data for the database

import bcrypt


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


# Default admin credentials
ADMINS_DATA = [
    {"login": "admin1", "password": "admin"},
]

# Levels data
LEVELS_DATA = [
    {"level_id": 1, "level_name": "weather"},
    {"level_id": 2, "level_name": "hellos, goodbyes"},
    {"level_id": 3, "level_name": "colors"},
    {"level_id": 4, "level_name": "animals"},
    {"level_id": 5, "level_name": "daily cycles"},
]

# Questions data (level_id -> questions)
QUESTIONS_DATA = [
    # Weather (level 1)
    {"question_id": 1, "level_id": 1, "question": "sunny"},
    {"question_id": 2, "level_id": 1, "question": "cloudy"},
    {"question_id": 3, "level_id": 1, "question": "windy"},
    {"question_id": 4, "level_id": 1, "question": "rainy"},
    {"question_id": 5, "level_id": 1, "question": "snowy"},
    {"question_id": 6, "level_id": 1, "question": "stormy"},

    # Hellos, goodbyes (level 2)
    {"question_id": 7, "level_id": 2, "question": "hello"},
    {"question_id": 8, "level_id": 2, "question": "good morning"},
    {"question_id": 9, "level_id": 2, "question": "goodbye"},
    {"question_id": 10, "level_id": 2, "question": "good night"},
    {"question_id": 11, "level_id": 2, "question": "see you later"},
    {"question_id": 12, "level_id": 2, "question": "bye"},

    # Colors (level 3)
    {"question_id": 13, "level_id": 3, "question": "red"},
    {"question_id": 14, "level_id": 3, "question": "orange"},
    {"question_id": 15, "level_id": 3, "question": "yellow"},
    {"question_id": 16, "level_id": 3, "question": "green"},
    {"question_id": 17, "level_id": 3, "question": "blue"},
    {"question_id": 18, "level_id": 3, "question": "violet"},
    {"question_id": 19, "level_id": 3, "question": "black"},
    {"question_id": 20, "level_id": 3, "question": "white"},
    {"question_id": 21, "level_id": 3, "question": "brown"},
    {"question_id": 22, "level_id": 3, "question": "gray"},

    # Animals (level 4)
    {"question_id": 33, "level_id": 4, "question": "cat"},

    # Daily cycles (level 5)
    {"question_id": 34, "level_id": 5, "question": "morning"},
]

# Answers data (question_id -> answers)
ANSWERS_DATA = [
    # Weather answers
    {"answer_id": 1, "question_id": 1, "answer": "sloneczny", "is_good": 1},
    {"answer_id": 2, "question_id": 1, "answer": "jasny", "is_good": 0},
    {"answer_id": 3, "question_id": 2, "answer": "mglisty", "is_good": 0},
    {"answer_id": 4, "question_id": 2, "answer": "pochmurny", "is_good": 1},
    {"answer_id": 5, "question_id": 3, "answer": "wietrzny", "is_good": 1},
    {"answer_id": 6, "question_id": 3, "answer": "sztormowy", "is_good": 0},
    {"answer_id": 7, "question_id": 4, "answer": "mokry", "is_good": 0},
    {"answer_id": 8, "question_id": 4, "answer": "deszczowy", "is_good": 1},
    {"answer_id": 9, "question_id": 5, "answer": "sniezny", "is_good": 1},
    {"answer_id": 10, "question_id": 5, "answer": "mrozny", "is_good": 0},
    {"answer_id": 11, "question_id": 6, "answer": "burzowy", "is_good": 1},
    {"answer_id": 12, "question_id": 6, "answer": "niespokojny", "is_good": 0},

    # Hellos, goodbyes answers
    {"answer_id": 13, "question_id": 7, "answer": "czesc", "is_good": 1},
    {"answer_id": 14, "question_id": 7, "answer": "witam", "is_good": 0},
    {"answer_id": 15, "question_id": 8, "answer": "dobrego ranka", "is_good": 0},
    {"answer_id": 16, "question_id": 8, "answer": "dzien dobry", "is_good": 1},
    {"answer_id": 17, "question_id": 9, "answer": "do widzenia", "is_good": 1},
    {"answer_id": 18, "question_id": 9, "answer": "trzymaj sie", "is_good": 0},
    {"answer_id": 19, "question_id": 10, "answer": "spij dobrze", "is_good": 0},
    {"answer_id": 20, "question_id": 10, "answer": "dobranoc", "is_good": 1},
    {"answer_id": 21, "question_id": 11, "answer": "do zobaczenia", "is_good": 1},
    {"answer_id": 22, "question_id": 11, "answer": "na razie", "is_good": 0},
    {"answer_id": 23, "question_id": 12, "answer": "czesc", "is_good": 1},
    {"answer_id": 24, "question_id": 12, "answer": "do jutra", "is_good": 0},

    # Colors answers
    {"answer_id": 25, "question_id": 13, "answer": "czerwony", "is_good": 1},
    {"answer_id": 26, "question_id": 13, "answer": "czarny", "is_good": 0},
    {"answer_id": 27, "question_id": 14, "answer": "pomaranczowy", "is_good": 1},
    {"answer_id": 28, "question_id": 14, "answer": "fioletowy", "is_good": 0},
    {"answer_id": 29, "question_id": 15, "answer": "zolty", "is_good": 1},
    {"answer_id": 30, "question_id": 15, "answer": "brazowy", "is_good": 0},
    {"answer_id": 31, "question_id": 16, "answer": "zielony", "is_good": 1},
    {"answer_id": 32, "question_id": 16, "answer": "bialy", "is_good": 0},
    {"answer_id": 33, "question_id": 17, "answer": "niebieski", "is_good": 1},
    {"answer_id": 34, "question_id": 17, "answer": "szary", "is_good": 0},
    {"answer_id": 35, "question_id": 18, "answer": "fioletowy", "is_good": 1},
    {"answer_id": 36, "question_id": 18, "answer": "czerwony", "is_good": 0},
    {"answer_id": 37, "question_id": 19, "answer": "czarny", "is_good": 1},
    {"answer_id": 38, "question_id": 19, "answer": "zolty", "is_good": 0},
    {"answer_id": 39, "question_id": 20, "answer": "bialy", "is_good": 1},
    {"answer_id": 40, "question_id": 20, "answer": "pomaranczowy", "is_good": 0},
    {"answer_id": 41, "question_id": 21, "answer": "brazowy", "is_good": 1},
    {"answer_id": 42, "question_id": 21, "answer": "zielony", "is_good": 0},
    {"answer_id": 43, "question_id": 22, "answer": "szary", "is_good": 1},
    {"answer_id": 44, "question_id": 22, "answer": "bialy", "is_good": 0},

    # Animals answers
    {"answer_id": 52, "question_id": 33, "answer": "kot", "is_good": 1},
    {"answer_id": 53, "question_id": 33, "answer": "pies", "is_good": 0},

    # Daily cycles answers
    {"answer_id": 54, "question_id": 34, "answer": "rano", "is_good": 1},
    {"answer_id": 55, "question_id": 34, "answer": "dzien", "is_good": 0},
    {"answer_id": 56, "question_id": 34, "answer": "noc", "is_good": 0},
    {"answer_id": 57, "question_id": 34, "answer": "wieczor", "is_good": 0},
]

# Sample users (for testing)
USERS_DATA = [
    {"login": "testuser", "password": "test123", "progress": 0},
]
