from telegram import Update
from telegram.ext import ContextTypes

from telegram import InlineKeyboardButton

from config import ROWS_PER_PAGE, COLS_PER_PAGE

from lang import Languages


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer(" ".join(update.callback_query.data.split(" ")[1:]))


def create_faq(faq: list, bot_username: str, caption: str, update: Update, page: int = 1) -> str:
    n = len(faq)
    if n == 0:
        text = Languages.msg("no_faq", update).format(bot_username=bot_username)
    else:
        max_rows = min(n, COLS_PER_PAGE)
        max_pages = (n + max_rows - 1) // max_rows

        page = max(page, 1)
        page = min(page, max_pages)

        if caption.strip():
            text = caption + ":"
        else:
            text = Languages.msg("faq", update).format(bot_username=bot_username)
        for i in range((page - 1) * max_rows, min(page * max_rows, n)):
            text += f"\n\n<b>{i + 1}.</b> {faq[i]['question']}"

    return text


def pagination(buttons, page, name, horizontal=False, additional_buttons=0):
    keyboard = []
    n = len(buttons)
    max_buttons = n
    if horizontal:
        max_buttons = min(n, COLS_PER_PAGE)
        keyboard = [[]]
    else:
        if n > ROWS_PER_PAGE - additional_buttons:
            max_buttons = ROWS_PER_PAGE - additional_buttons - 1

    max_pages = 1
    if max_buttons > 0:
        max_pages = (n + max_buttons - 1) // max_buttons

        page = max(page, 1)
        page = min(page, max_pages)

        for i in range((page - 1) * max_buttons, min(page * max_buttons, n)):
            if horizontal:
                keyboard[0].append(buttons[i])
            else:
                if isinstance(buttons[i], list):
                    keyboard.append(buttons[i])
                else:
                    keyboard.append([buttons[i]])

    if max_pages > 1:
        pages_str = f"{page}/{max_pages}"
        keyboard.append([
             InlineKeyboardButton("⬅️", callback_data=f"{name}_page {page - 1}"),
             InlineKeyboardButton(pages_str, callback_data=f"callback {pages_str}"),
             InlineKeyboardButton("➡️", callback_data=f"{name}_page {page + 1}")
        ])

    return keyboard


def filter_faq(faq: list, search: str) -> list:
    return [question for question in faq if search.lower() in question["question"].lower()]