from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import COLS_PER_PAGE


def faq(bot_obj, add=False) -> InlineKeyboardMarkup:
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