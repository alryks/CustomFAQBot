from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import COLS_PER_PAGE


def faq(bot_obj: dict, add: bool = False) -> InlineKeyboardMarkup:
    keyboard = []
    faq = bot_obj["faq"]
    bot_id = bot_obj["_id"]
    if len(faq) > 0:
        for i in range(len(faq)):
            button = InlineKeyboardButton(f"{i + 1}", callback_data=f"faq_ans {bot_id} {i}")
            if i % COLS_PER_PAGE == 0:
                keyboard.append([button])
            else:
                keyboard[-1].append(button)

    if add:
        keyboard.append([InlineKeyboardButton("➕Add Question", callback_data=f"faq_add {bot_id}")])
    keyboard.append([InlineKeyboardButton("✖️Cancel", callback_data="cancel")])

    return InlineKeyboardMarkup(keyboard)


def accept_deny(bot_obj: dict, user_id: int, is_admin=False) -> InlineKeyboardMarkup:
    access_type = "admin" if is_admin else "user"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅", callback_data=f"accept_{access_type} {bot_obj['_id']} {user_id}"), InlineKeyboardButton("❌", callback_data="cancel")]
    ])