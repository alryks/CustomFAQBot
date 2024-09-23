"""
add is_temp field to all users
"""

from config import DB

DB.users.update_many({}, {"$set": {"is_temp": False}})