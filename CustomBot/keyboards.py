from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup

from misc import pagination


def faq(bot_obj: dict, edit: bool = False, page: int = 1) -> InlineKeyboardMarkup:
    question_type = "edit" if edit else "ans"
    buttons = []
    faq = bot_obj["faq"]
    for i in range(len(faq)):
        button = InlineKeyboardButton(f"{i + 1}", callback_data=f"faq_{question_type} {faq[i]['_id']}")
        buttons.append(button)

    keyboard = pagination(buttons, page, f"faq_{question_type}",
                          horizontal=True, additional_buttons=1 + int(edit))

    if edit:
        keyboard.append([InlineKeyboardButton("➕Add Question", callback_data=f"faq_add")])
    keyboard.append([InlineKeyboardButton("✖️Cancel", callback_data="cancel")])

    return InlineKeyboardMarkup(keyboard)


def stop_answer() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[f"🛑Stop answering"], ["❌Cancel"]],
                               resize_keyboard=True,
                               one_time_keyboard=True)


def accept_deny(bot_obj: dict, user_id: int, is_admin=False) -> InlineKeyboardMarkup:
    access_type = "admin" if is_admin else "user"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅", callback_data=f"accept_{access_type} {bot_obj['_id']} {user_id}"), InlineKeyboardButton("❌", callback_data="cancel")]
    ])