from dotenv import dotenv_values

import pymongo

from CustomBot.bot import Bot

config = dotenv_values(".env")

# Telegram Bot
BOT_TOKEN = config["BOT_TOKEN"]
BOT = Bot(BOT_TOKEN)

ROWS_PER_PAGE = 10
COLS_PER_PAGE = 5

# Database
DB_USER = config["DB_USER"]
DB_PASS = config["DB_PASS"]
DB_HOST = config["DB_HOST"]
DB_PORT = config["DB_PORT"]

DB_NAME = config["DB_NAME"]

DB = pymongo.MongoClient(f"mongodb://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}")[DB_NAME]