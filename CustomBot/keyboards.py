from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup

from bson import ObjectId

from misc import pagination


def faq(bot_faq: list, edit: bool = False, page: int = 1) -> InlineKeyboardMarkup:
    question_type = "edit" if edit else "ans"
    buttons = []
    for i in range(len(bot_faq)):
        button = InlineKeyboardButton(f"{i + 1}", callback_data=f"faq_{question_type} {bot_faq[i]['_id']}")
        buttons.append(button)

    keyboard = pagination(buttons, page, f"faq_{question_type}",
                          horizontal=True, additional_buttons=1 + int(edit))

    if edit:
        keyboard.append([InlineKeyboardButton("➕Add Question", callback_data=f"faq_add")])
    keyboard.append([InlineKeyboardButton("✖️Cancel", callback_data="cancel")])

    return InlineKeyboardMarkup(keyboard)


def stop_answer() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[f"🛑Stop answering"], ["✖️Cancel"]],
                               resize_keyboard=True,
                               one_time_keyboard=True)


def faq_edit(question_id: ObjectId) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️Edit", callback_data=f"question_edit {question_id}"),
         InlineKeyboardButton("❌Delete", callback_data=f"question_delete {question_id}")],
        [InlineKeyboardButton("🔙Back", callback_data="question_back")]
    ])


def accept_deny(bot_obj: dict, user_id: int, is_admin=False) -> InlineKeyboardMarkup:
    access_type = "admin" if is_admin else "user"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅", callback_data=f"accept_{access_type} {bot_obj['_id']} {user_id}"), InlineKeyboardButton("❌", callback_data="cancel")]
    ])