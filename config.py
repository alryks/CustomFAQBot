from dotenv import dotenv_values

import pymongo

config = dotenv_values(".env")

# Logging
SPREADSHEET_ID = config["SPREADSHEET_ID"]
SPREADSHEET_RANGE = config["SPREADSHEET_RANGE"]

# Telegram Bot
BOT_TOKEN = config["BOT_TOKEN"]
PARSE_MODE = "HTML"
PRIVATE = True

# Friend API
FRIEND_API = "localhost:8000"

HELP_MESSAGE = None
HELP_MESSAGE_CHAT = None

ROWS_PER_PAGE = 10
COLS_PER_PAGE = 5

# Fields
FIELDS = {
    "name": "",
    "supervisor": None,
    "job_title": "",
    "unit": "",
    "place": "",
    "personal_phone": "",
    "work_phone": "",
    "additional_number": 0,
    "email": "",
    "tg_id": 0,
    "access": []
}
REQUIRED_FIELDS = ["name", "personal_phone"]

USER_ACCESS = ["faq", "contacts"]
ADMIN_ACCESS = ["faq_mod", "contacts_mod", "report", "request"]

# Database
DB_USER = config["DB_USER"]
DB_PASS = config["DB_PASS"]
DB_HOST = config["DB_HOST"]
DB_PORT = config["DB_PORT"]

DB_NAME = config["DB_NAME"]

DB = pymongo.MongoClient(f"mongodb://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}")[DB_NAME]
