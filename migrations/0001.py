"""
migration file to add "required_fields" (dict) field in bots collection, where:
required_fields = {
    "name": True,
    "job_title": False,
    "unit": False,
    "place": False,
    "phone": False,
    "email": False
}
as default value if "required_fields" field is not present in the bot object
"""

from config import DB

bots = DB.bots.find()
for bot in bots:
    if "required_fields" not in bot:
        DB.bots.update_one({"_id": bot["_id"]}, {"$set": {"required_fields": {
            "name": True,
            "job_title": False,
            "unit": False,
            "place": False,
            "phone": False,
            "email": False
        }}})