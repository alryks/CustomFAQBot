from typing import Optional

from telegram.error import TelegramError

from telegram import Update, Bot
from telegram.ext import ContextTypes

from telegram import InlineKeyboardButton

from config import ROWS_PER_PAGE, COLS_PER_PAGE, REQUIRED_FIELDS

from lang import Languages

from verify_email import verify_email_async
import phonenumbers

from db import UsersDb


def parse_phone(phone: str) -> Optional[str]:
    try:
        number: Optional[phonenumbers.PhoneNumber] = phonenumbers.parse(phone, phonenumbers.phonenumberutil.region_code_for_country_code(7))
    except phonenumbers.phonenumberutil.NumberParseException:
        return None
    if not phonenumbers.is_valid_number(number):
        return None
    return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)


async def check_email(email: str) -> bool:
    return await verify_email_async(email)


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer(" ".join(update.callback_query.data.split(" ")[1:]))


def create_faq(faq: list, update: Update, page: int = 1) -> str:
    n = len(faq)
    if n == 0:
        text = Languages.msg("empty", update)
    else:
        max_rows = min(n, COLS_PER_PAGE)
        max_pages = (n + max_rows - 1) // max_rows

        page = max(page, 1)
        page = min(page, max_pages)

        text = Languages.msg("faq", update)

        for i in range((page - 1) * max_rows, min(page * max_rows, n)):
            text += f"\n\n<b>{i + 1}.</b> {faq[i]['question']}"

    return text


async def create_contacts(users: list, bot: Bot, update: Update, page: int = 1, which: str = "contacts") -> str:
    n = len(users)
    if n == 0:
        text = Languages.msg("empty", update)
    else:
        max_rows = min(n, COLS_PER_PAGE)
        max_pages = (n + max_rows - 1) // max_rows

        page = max(page, 1)
        page = min(page, max_pages)

        if which == "similar":
            text = Languages.msg("similar_users", update)
        elif which == "contacts":
            text = Languages.msg("contacts_caption", update)
        elif which == "supervisors":
            text = Languages.msg("supervisors", update)

        for i in range((page - 1) * max_rows, min(page * max_rows, n)):
            if users[i].get("name", "") == "":
                chat = await bot.get_chat(users[i]["tg_id"])
                username = chat.full_name + (f" @{chat.username}" if chat.username else "")
                text += f"\n\n<b>{i + 1}.</b> {username}"
            else:
                text += f"\n\n<b>{i + 1}.</b> {users[i]['name']}"
                if users[i].get("job_title", "") != "":
                    text += f" – <i>{users[i]['job_title']}</i>"

    return text


def pagination(buttons, page, name, horizontal=False, additional_buttons=0, additional_info=""):
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
        if additional_info:
            keyboard.append([
                InlineKeyboardButton("⬅️", callback_data=f"{name}_page {additional_info} {page - 1}"),
                InlineKeyboardButton(pages_str, callback_data=f"callback {pages_str}"),
                InlineKeyboardButton("➡️", callback_data=f"{name}_page {additional_info} {page + 1}")
            ])
        else:
            keyboard.append([
                 InlineKeyboardButton("⬅️", callback_data=f"{name}_page {page - 1}"),
                 InlineKeyboardButton(pages_str, callback_data=f"callback {pages_str}"),
                 InlineKeyboardButton("➡️", callback_data=f"{name}_page {page + 1}")
            ])

    return keyboard


async def user_info(user_obj: dict, update: Update, bot: Bot) -> str:
    general_info = ""
    if user_obj.get("name", "") != "":
        general_info += Languages.msg("name", update).format(
            name=user_obj["name"]) + "\n"
    if user_obj.get("supervisor", None) is not None:
        supervisor_obj = UsersDb.get_user(user_obj["supervisor"])
        if supervisor_obj:
            general_info += Languages.msg("supervisor", update).format(
                supervisor=supervisor_obj["name"]) + "\n"
    if user_obj.get("job_title", "") != "":
        general_info += Languages.msg("job_title", update).format(
            job_title=user_obj["job_title"]) + "\n"
    if user_obj.get("unit", "") != "":
        general_info += Languages.msg("unit", update).format(
            unit=user_obj["unit"]) + "\n"
    if user_obj.get("place", "") != "":
        general_info += Languages.msg("place", update).format(
            place=user_obj["place"]) + "\n"

    contacts = ""
    if user_obj.get("personal_phone", "") != "":
        contacts += Languages.msg("personal_phone", update).format(
            phone=user_obj["personal_phone"]) + "\n"
    if user_obj.get("work_phone", "") != "":
        contacts += Languages.msg("work_phone", update).format(
            phone=user_obj["work_phone"]) + "\n"
    if user_obj.get("additional_number", 0) != 0:
        contacts += Languages.msg("additional_number", update).format(
            number=user_obj["additional_number"]) + "\n"
    if user_obj.get("email", "") != "":
        contacts += Languages.msg("email", update).format(
            email=user_obj["email"]) + "\n"
    if user_obj.get("tg_id", 0) != 0:
        try:
            chat = await bot.get_chat(user_obj["tg_id"])
            username = chat.full_name + (f" @{chat.username}" if chat.username else "")
            contacts += Languages.msg("telegram", update).format(telegram=username) + "\n"
        except TelegramError:
            pass

    if general_info == "":
        text = f'{Languages.msg("contacts", update)}\n{contacts}'
    elif contacts == "":
        text = f'{Languages.msg("general_info", update)}\n{general_info}'
    else:
        text = f'{Languages.msg("general_info", update)}\n{general_info}\n{Languages.msg("contacts", update)}\n{contacts}'

    return text


def filter_faq(faq: list, search: str) -> list:
    if not search:
        return faq
    search = search.lower()
    filtered = []
    for question in faq:
        # Поиск по тексту вопроса
        if search in question["question"].lower():
            filtered.append(question)
            continue
            
        # Поиск по тексту ответов
        for answer in question["answers"]:
            if "text" in answer and search in answer["text"].lower():
                filtered.append(question)
                break
                
    return filtered


def filter_contacts(users: list, required_fields: list) -> list:
    # return [user for user in users if all(user.get(field, "") != "" for field in required_fields)]
    return [user for user in users if user.get(required_fields[0], "") != ""]


def search_contacts(users: list, search: str) -> list:
    results_by_field = {
        "name": [],
        "supervisor": [],
        "job_title": [],
        "unit": [],
        "place": [],
        "personal_phone": [],
        "work_phone": [],
        "additional_number": [],
        "email": []
    }
    result = []
    for user in users:
        supervisor = UsersDb.get_user(user["supervisor"])
        if search.lower() in user.get("name", "").lower():
            results_by_field["name"].append(user)
        elif supervisor and search.lower() in supervisor.get("name", "").lower():
            results_by_field["supervisor"].append(user)
        elif search.lower() in user.get("job_title", "").lower():
            results_by_field["job_title"].append(user)
        elif search.lower() in user.get("unit", "").lower():
            results_by_field["unit"].append(user)
        elif search.lower() in user.get("place", "").lower():
            results_by_field["place"].append(user)
        elif search.lower() in user.get("personal_phone", "").lower():
            results_by_field["personal_phone"].append(user)
        elif search.lower() in user.get("work_phone", "").lower():
            results_by_field["work_phone"].append(user)
        elif user.get("additional_number", 0) and search.lower() in str(user.get("additional_number", 0)).lower():
            results_by_field["additional_number"].append(user)
        elif search.lower() in user.get("email", "").lower():
            results_by_field["email"].append(user)
    field = "name" if not REQUIRED_FIELDS else REQUIRED_FIELDS[0]
    for key, value in results_by_field.items():
        result += sort_contacts(value, field)

    return result


def sort_contacts(users: list, field: str) -> list:
    return sorted(users, key=lambda user: user.get(field, "").lower())
