import phonenumbers
from typing import Optional

def parse_phone(phone: str) -> Optional[str]:
    try:
        number: Optional[phonenumbers.PhoneNumber] = phonenumbers.parse(phone, phonenumbers.phonenumberutil.region_code_for_country_code(7))
    except phonenumbers.phonenumberutil.NumberParseException:
        return None
    if not phonenumbers.is_valid_number(number):
        return None
    return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)


"""
go through all users and parse its phone and rewrite it in given format in database
"""

from config import DB

for user in DB.users.find():
    phone = parse_phone(user["personal_phone"])
    if phone:
        print(f"Valid phone: {phone}")
        DB.users.update_one({"_id": user["_id"]}, {"$set": {"personal_phone": phone}})
    else:
        if user["personal_phone"] != "":
            print(f"Invalid phone: {user['personal_phone']}")