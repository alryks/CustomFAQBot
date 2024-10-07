"""
migration file to do following:
for each user in "users" collection do following:
1. if user["is_temp"] is True then set user["access"] to []
2. else if user["is_admin"] is True then set user["access"] to ["faq", "contacts", "faq_mod", "contacts_mod", "report", "request"]
3. else set user["access"] to ["faq", "contacts"]
4. remove user["is_temp"] and user["is_admin"] fields
"""

from config import DB

for user in DB.users.find():
    access = []
    if not user["is_temp"]:
        access.extend(["faq", "contacts"])
        if user["is_admin"]:
            access.extend(["faq_mod", "contacts_mod", "report", "request"])

    DB.users.update_one({"_id": user["_id"]}, {"$set": {"access": access}, "$unset": {"is_temp": "", "is_admin": ""}})