"""
migration file to go through all bots and through all users of each bot and
set "is_admin" field to False if it is not in bots.admins list else to True
and then remove bots.admins list
"""

from config import DB

bots = DB.bots.find()
for bot in bots:
    admins = bot.get("admins", [])
    for user in bot["users"]:
        if "is_admin" not in user:
            DB.bots.update_one({"_id": bot["_id"], "users._id": user["_id"]}, {"$set": {"users.$.is_admin": user["tg_id"] in admins}})
    DB.bots.update_one({"_id": bot["_id"]}, {"$unset": {"admins": ""}})