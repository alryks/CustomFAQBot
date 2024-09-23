"""
add work_phone, additional_number and supervisor fields to all users
"""

from config import DB

DB.users.update_many({}, {"$set": {"work_phone": "", "additional_number": 0, "supervisor": None}})