from typing import Union

from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup

from telegram.ext import ExtBot

from bson import ObjectId

from misc import pagination

from lang import Languages


def faq(bot_faq: list, update: Update, edit: bool = False, page: int = 1) -> InlineKeyboardMarkup:
    buttons = []
    for i in range(len(bot_faq)):
        button = InlineKeyboardButton(f"{i + 1}", callback_data=f"faq {bot_faq[i]['_id']}")
        buttons.append(button)

    keyboard = pagination(buttons, page, f"faq",
                          horizontal=True, additional_buttons=1 + int(edit) * 2)

    if edit:
        keyboard.append([InlineKeyboardButton(Languages.kbd("edit_caption", update), callback_data=f"caption")])
        keyboard.append([InlineKeyboardButton(Languages.kbd("add_question", update), callback_data=f"faq_add")])
    keyboard.append([InlineKeyboardButton(Languages.kbd("cancel", update), callback_data="cancel")])

    return InlineKeyboardMarkup(keyboard)


def faq_edit(question_id: ObjectId, update: Update) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(Languages.kbd("edit", update), callback_data=f"question_edit {question_id}"),
         InlineKeyboardButton(Languages.kbd("delete", update), callback_data=f"question_delete {question_id}")],
        [InlineKeyboardButton(Languages.kbd("cancel", update), callback_data="question_cancel")]
    ])


def contacts(users: list, edit: bool, update: Update, page: int = 1) -> InlineKeyboardMarkup:
    buttons = []
    for i in range(len(users)):
        button = InlineKeyboardButton(f"{i + 1}", callback_data=f"user {users[i]['_id']}")
        buttons.append(button)

    keyboard = pagination(buttons, page, "contacts", horizontal=True, additional_buttons=1 + int(edit))

    if edit:
        keyboard.append([InlineKeyboardButton(Languages.kbd("add_user", update), callback_data="contacts_add")])

    keyboard.append([InlineKeyboardButton(Languages.kbd("cancel", update), callback_data="cancel")])

    return InlineKeyboardMarkup(keyboard)


def user(user_obj: dict, admin: bool, update: Update, is_merge: bool) -> InlineKeyboardMarkup:
    user_id = user_obj["_id"]
    keyboard = [
        [
            InlineKeyboardButton(Languages.kbd("edit_user_name", update), callback_data=f"user_name {user_id}"),
            InlineKeyboardButton(Languages.kbd("edit_job_title", update), callback_data=f"user_job_title {user_id}")
        ],
        [
            InlineKeyboardButton(Languages.kbd("edit_unit", update),  callback_data=f"user_unit {user_id}"),
            InlineKeyboardButton(Languages.kbd("edit_place", update), callback_data=f"user_place {user_id}")
        ],
        [
            InlineKeyboardButton(Languages.kbd("edit_phone", update), callback_data=f"user_phone {user_id}"),
            InlineKeyboardButton(Languages.kbd("edit_email", update), callback_data=f"user_email {user_id}")
        ]
    ]
    admin_buttons = []
    if admin:
        admin_buttons.append(
                InlineKeyboardButton(Languages.kbd("user_admin", update).format(admin="✅" if user_obj["is_admin"] else "❌"), callback_data=f"user_admin {user_id}")
        )
    admin_buttons.append(
        InlineKeyboardButton(Languages.kbd("merge", update),
                             callback_data=f"user_merge {user_id}") if is_merge else InlineKeyboardButton(Languages.kbd("unmerge", update), callback_data=f"user_unmerge {user_id}")
    )
    keyboard.append(admin_buttons)
    keyboard.extend([
        [
            InlineKeyboardButton(Languages.kbd("delete", update), callback_data=f"user_delete {user_id}")
        ],
        [
            InlineKeyboardButton(Languages.kbd("back", update), callback_data=f"user_back")
        ],
    ])

    return InlineKeyboardMarkup(keyboard)


async def user_merge(user_id: ObjectId, bot: ExtBot, users: [dict], page: int, update: Update) -> InlineKeyboardMarkup:
    buttons = []
    for bot_user in users:
        if bot_user.get("name", "") != "":
            name = bot_user["name"]
        else:
            chat = await bot.get_chat(bot_user["tg_id"])
            name = chat.full_name + (f" @{chat.username}" if chat.username else "")
        buttons.append([InlineKeyboardButton(name, callback_data=f"users_merge {user_id} {bot_user['_id']}")])

    keyboard = pagination(buttons, page, "user_merge", additional_buttons=1)

    keyboard.append([InlineKeyboardButton(Languages.kbd("back", update), callback_data=f"merge_back {user_id}")])

    return InlineKeyboardMarkup(keyboard)


def reset(update: Update) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[Languages.btn("reset", update)], [Languages.btn("cancel", update)]],
                               resize_keyboard=True,
                               one_time_keyboard=True)


def stop_answer(update: Update) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[Languages.btn("stop_answer", update)], [Languages.btn("cancel", update)]],
                               resize_keyboard=True,
                               one_time_keyboard=True)


def accept_deny(bot_obj: dict, user_id: Union[int, ObjectId]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅", callback_data=f"accept {user_id}"), InlineKeyboardButton("❌", callback_data=f"deny {user_id}")],
    ])