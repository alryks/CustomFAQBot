from typing import Union, Optional

from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup

from bson import ObjectId

from misc import pagination

from lang import Languages


def cancel(update: Update) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[Languages.btn("cancel", update)]],
                               resize_keyboard=True,
                               one_time_keyboard=True)


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


def contacts(users: list, edit: bool, update: Update, page: int = 1, similar: bool = False, user_id: Optional[ObjectId] = None) -> InlineKeyboardMarkup:
    buttons = []
    callback_data = "similar" if similar else "user"
    for i in range(len(users)):
        callback_data_user = f"{callback_data} {users[i]['_id']}"
        if similar:
            callback_data_user += f" {user_id}"
        button = InlineKeyboardButton(f"{i + 1}", callback_data=callback_data_user)
        buttons.append(button)

    page_name = "similar" if similar else "contacts"

    keyboard = pagination(buttons, page, page_name, horizontal=True, additional_buttons=1 + int(edit), additional_info=user_id if similar else "")

    if edit:
        keyboard.append([InlineKeyboardButton(Languages.kbd("add_user", update), callback_data="contacts_add")])

    if not similar:
        keyboard.append([InlineKeyboardButton(Languages.kbd("cancel", update), callback_data="cancel")])
    else:
        keyboard.append([InlineKeyboardButton(Languages.kbd("to_user", update), callback_data=f"user {user_id}")])

    return InlineKeyboardMarkup(keyboard)


def user(user_obj: dict, admin: bool, update: Update) -> InlineKeyboardMarkup:
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
    if admin:
        keyboard.append([
                InlineKeyboardButton(Languages.kbd("user_admin", update).format(admin="✅" if user_obj["is_admin"] else "❌"), callback_data=f"user_admin {user_id}")
        ])
    keyboard.extend([
        [
            InlineKeyboardButton(Languages.kbd("delete", update), callback_data=f"user_delete {user_id}")
        ],
        [
            InlineKeyboardButton(Languages.kbd("cancel", update), callback_data=f"user_cancel")
        ],
    ])

    return InlineKeyboardMarkup(keyboard)


def confirm_delete(update: Update, user_obj: dict) -> InlineKeyboardMarkup:
    user_id = user_obj["_id"]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(Languages.kbd("delete", update), callback_data=f"user_confirm_delete {user_id}"),
         InlineKeyboardButton(Languages.kbd("cancel", update), callback_data="cancel")]
    ])


def reset(update: Update) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[Languages.btn("reset", update)], [Languages.btn("cancel", update)]],
                               resize_keyboard=True,
                               one_time_keyboard=True)


def stop_answer(update: Update) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[Languages.btn("stop_answer", update)], [Languages.btn("cancel", update)]],
                               resize_keyboard=True,
                               one_time_keyboard=True)


def accept_deny(user_id: Union[int, ObjectId]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅", callback_data=f"accept {user_id}"), InlineKeyboardButton("❌", callback_data=f"deny {user_id}")],
    ])