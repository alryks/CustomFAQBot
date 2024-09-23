"""
replace phone field with personal_phone field in all users
"""

from config import DB

DB.users.update_many({}, {"$rename": {"phone": "personal_phone"}})