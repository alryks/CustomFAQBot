"""
migration to copy "users" collection to "users" collection and
"faq" collection to "faq" collection from the first bot
"""

from config import DB

bot = DB.bots.find_one()
users = bot["users"]
faq = bot["faq"]

DB.users.insert_many(users)
DB.faq.insert_many(faq)