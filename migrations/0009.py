"""
for every answer in "faq" collection add text field
"""

from config import DB

for question in DB.faq.find():
    answers = question["answers"]
    for answer in answers:
        answer["text"] = ""
    for answer in answers:
        print(answer)
    DB.faq.update_one({"_id": question["_id"]}, {"$set": {"answers": answers}})
