from dotenv import dotenv_values

import pymongo

config = dotenv_values(".env")

# Telegram Bot
BOT_TOKEN = config["BOT_TOKEN"]
PARSE_MODE = "HTML"
PRIVATE = True

ROWS_PER_PAGE = 10
COLS_PER_PAGE = 5

# Fields
FIELDS = {
    "name": "",
    "supervisor": "",
    "job_title": "",
    "unit": "",
    "place": "",
    "phone": "",
    "email": "",
    "tg_id": 0,
    "is_admin": False,
    "is_temp": False
}
REQUIRED_FIELDS = ["name"]

# Database
DB_USER = config["DB_USER"]
DB_PASS = config["DB_PASS"]
DB_HOST = config["DB_HOST"]
DB_PORT = config["DB_PORT"]

DB_NAME = config["DB_NAME"]

DB = pymongo.MongoClient(f"mongodb://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}")[DB_NAME]
