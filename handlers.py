from typing import Optional

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes

from bson import ObjectId

from config import PARSE_MODE, PRIVATE, FIELDS, REQUIRED_FIELDS, USER_ACCESS, ADMIN_ACCESS, HELP_MESSAGE_CHAT, HELP_MESSAGE

from log import log_action

import keyboards

from db import ReportsDb, UsersDb, FaqDb

from state import State

from misc import create_faq, filter_faq, \
    create_contacts, search_contacts, filter_contacts, \
    user_info, parse_phone, check_email

from lang import Languages


async def check_user(update: Update, context: ContextTypes.DEFAULT_TYPE, access: str, send: bool = True) -> bool:
    if access in ADMIN_ACCESS:
        user_obj = UsersDb.get_user_by_tg(update.effective_user.id)
        if user_obj and access in user_obj["access"]:
            return True

        if send:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("not_admin", update),
                parse_mode=PARSE_MODE,
            )

        return False

    if not PRIVATE:
        return True

    user_obj = UsersDb.get_user_by_tg(update.effective_user.id)
    if user_obj and access in user_obj["access"]:
        return True

    if not send:
        return False

    if user_obj and not user_obj["access"]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("already_requested", update),
            parse_mode=PARSE_MODE,
        )
        return False

    log_action(update.effective_user, "unregistered", access)

    if not REQUIRED_FIELDS:
        user = FIELDS.copy()
        user.update({
            "tg_id": update.effective_user.id,
            "access": [],
        })
        user_id = UsersDb.add_user(user)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("not_user_request", update),
            parse_mode=PARSE_MODE,
        )

        user_obj = UsersDb.get_user(user_id)

        for admin in UsersDb.get_users_by_access("request"):
            try:
                if admin["tg_id"] == 0:
                    continue

                await context.bot.send_message(
                    chat_id=admin["tg_id"],
                    text=Languages.msg("request_user", update).format(data=user_info(user_obj, update, context.bot)),
                    reply_markup=keyboards.accept_deny(user_id),
                    parse_mode=PARSE_MODE,
                )
            except:
                pass

        return False

    first_field = REQUIRED_FIELDS[0]
    context.user_data["state"] = State[first_field.upper()].name

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("register", update),
        parse_mode=PARSE_MODE,
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_" + first_field, update),
        reply_markup=keyboards.cancel(update),
        parse_mode=PARSE_MODE,
    )

    return False


async def accept(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    if not await check_user(update, context, "request"):
        context.user_data["edit"] = False
        return

    user_obj = UsersDb.get_user(ObjectId(update.callback_query.data.split(" ")[1]))

    if user_obj and not user_obj["access"]:
        UsersDb.edit_user(user_obj["_id"], {"access": USER_ACCESS})
        await context.bot.send_message(
            chat_id=user_obj["tg_id"],
            text=Languages.msg("user_accepted", update),
            parse_mode=PARSE_MODE,
        )
        await context.bot.send_message(
            chat_id=user_obj["tg_id"],
            text=Languages.msg("help", update),
            parse_mode=PARSE_MODE,
        )

        log_action(update.effective_user, "accept", user_obj["tg_id"])

        context.user_data["edit"] = True

        await similar(update, context, user_id=user_obj["_id"])


async def similar(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: Optional[ObjectId] = None, delete: bool = False, page: int = 1) -> None:
    if not await check_user(update, context, "contacts_mod", send=False):
        context.user_data["edit"] = False
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        await contacts(update, context)
        return

    if delete:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )

    if not user_id:
        user_id = ObjectId(update.callback_query.data.split(" ")[2])
    similar_users = UsersDb.get_similar_users(user_id, REQUIRED_FIELDS[0])
    if not similar_users:
        return await contact(update, context, user_id=user_id)

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=await create_contacts(similar_users, context.bot, update, page, which="similar"),
        reply_markup=keyboards.contacts(similar_users, False, update, page, which="similar", user_id=user_id),
        parse_mode=PARSE_MODE,
    )
    if not context.user_data.get("delete_message_ids"):
        context.user_data["delete_message_ids"] = []
    context.user_data["delete_message_ids"].append(message.message_id)


async def similar_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await similar(update, context, delete=True, page=int(update.callback_query.data.split(" ")[2]), user_id=ObjectId(update.callback_query.data.split(" ")[1]))


async def similar_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context, "contacts_mod", send=False):
        context.user_data["edit"] = False
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        await contacts(update, context)
        return

    user_obj = UsersDb.get_user(ObjectId(update.callback_query.data.split(" ")[2]))
    tg_id = user_obj["tg_id"]

    user_id = ObjectId(update.callback_query.data.split(" ")[1])
    UsersDb.edit_user(user_id, {"tg_id": tg_id})

    UsersDb.delete_user(user_obj["_id"])

    await contact(update, context, user_id=user_id)


async def deny(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    if not await check_user(update, context, "request"):
        context.user_data["edit"] = False
        return

    user_obj = UsersDb.get_user(ObjectId(update.callback_query.data.split(" ")[1]))

    if user_obj and not user_obj["access"]:
        await context.bot.send_message(
            chat_id=user_obj["tg_id"],
            text=Languages.msg("user_denied", update),
            parse_mode=PARSE_MODE,
        )
        UsersDb.delete_user(user_obj["_id"])

        log_action(update.effective_user, "deny", user_obj["tg_id"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["search"] = None
    context.user_data["state"] = State.IDLE.name

    if not await check_user(update, context, "faq", send=False):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("help_unregistered", update),
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=PARSE_MODE,
        )
        await check_user(update, context, "faq")
        return

    if not HELP_MESSAGE or not HELP_MESSAGE_CHAT:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("help", update),
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=PARSE_MODE,
        )
    else:
        await context.bot.copy_message(
            chat_id=update.effective_chat.id,
            from_chat_id=HELP_MESSAGE_CHAT,
            message_id=HELP_MESSAGE
        )
    
    log_action(update.effective_user, "start")


async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context, "faq_mod"):
        return

    context.user_data["edit"] = not context.user_data.get("edit", False)

    if context.user_data["edit"]:
        message = Languages.msg("edit_true", update)
    else:
        message = Languages.msg("edit_false", update)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode=PARSE_MODE,
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )


async def delete_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    delete_message_ids = context.user_data.get("delete_message_ids")
    if delete_message_ids is not None:
        for delete_message_id in delete_message_ids:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=delete_message_id
                )
            except:
                pass

    context.user_data["delete_message_ids"] = []


async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE, delete=False, page=1) -> None:
    context.user_data["state"] = State.FAQ.name

    if not await check_user(update, context, "faq"):
        return

    if context.user_data.get("edit", False):
        if not await check_user(update, context, "faq_mod", send=False):
            context.user_data["edit"] = False

    search = context.user_data.get("search")
    if search is None:
        search = ""

    log_action(update.effective_user, "faq", search, page)

    filtered_faq = filter_faq(FaqDb.get_faq(), search)

    text = create_faq(filtered_faq, update, page)

    if delete:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=keyboards.faq(filtered_faq, update, context.user_data.get("edit", False), page),
        parse_mode=PARSE_MODE,
    )


async def faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["search"] = None
    await faq(update, context)


async def faq_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await faq(update, context, delete=True, page=int(update.callback_query.data.split(" ")[1]))


async def faq_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context, "faq_mod", send=False):
        context.user_data["edit"] = False
        await faq(update, context, delete=True)
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_question", update),
        reply_markup=keyboards.cancel(update),
        parse_mode=PARSE_MODE,
    )

    context.user_data["state"] = State.ADD_QUESTION.name

    if update.callback_query:
        await update.callback_query.answer(
            text=Languages.msg("answer_sent", update),
        )


async def faq_ans(update: Update, context: ContextTypes.DEFAULT_TYPE, question_id: Optional[ObjectId] = None) -> None:
    if not await check_user(update, context, "faq"):
        return

    if not question_id:
        question_id = ObjectId(update.callback_query.data.split(" ")[1])

    question = FaqDb.get_question(question_id)
    if not question:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.callback_query.message.message_id,
        )
        await faq(update, context)
        return
    answers = question["answers"]

    log_action(update.effective_user, "faq_ans", question["question"])

    await delete_messages(update, context)

    if context.user_data.get("edit", False):
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("current_question", update).format(question=question["question"]),
            parse_mode=PARSE_MODE,
        )
        context.user_data["delete_message_ids"].append(message.message_id)

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("current_answers", update),
            parse_mode=PARSE_MODE,
        )
        context.user_data["delete_message_ids"].append(message.message_id)

    for answer in answers:
        message = await context.bot.copy_message(
            chat_id=update.effective_chat.id,
            from_chat_id=answer["chat_id"],
            message_id=answer["message_id"],
        )
        context.user_data["delete_message_ids"].append(message.message_id)

    if context.user_data.get("edit", False):
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("question_action", update),
            reply_markup=keyboards.faq_edit(question["_id"], update),
            parse_mode=PARSE_MODE,
        )
        context.user_data["delete_message_ids"].append(message.message_id)

    if update.callback_query:
        await update.callback_query.answer(
            text=Languages.msg("answer_sent", update),
        )


async def question_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context, "faq_mod", send=False):
        context.user_data["edit"] = False

        await delete_messages(update, context)

        await faq(update, context)
        return

    context.user_data["question_id"] = ObjectId(update.callback_query.data.split(" ")[1])
    context.user_data["state"] = State.EDIT_QUESTION.name

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_new_question", update),
        reply_markup=keyboards.cancel(update),
        parse_mode=PARSE_MODE,
    )


async def question_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context, "faq_mod", send=False):
        context.user_data["edit"] = False

        await delete_messages(update, context)

        await faq(update, context)
        return

    question_id = ObjectId(update.callback_query.data.split(" ")[1])
    FaqDb.delete_question(question_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("question_deleted", update),
        parse_mode=PARSE_MODE,
    )

    await delete_messages(update, context)

    await faq(update, context)


async def question_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await delete_messages(update, context)

    if not await check_user(update, context, "faq_mod", send=False):
        context.user_data["edit"] = False
        await faq(update, context)
        return


async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE, delete: bool = False, page: int = 1) -> None:
    context.user_data["state"] = State.CONTACTS.name

    if not await check_user(update, context, "contacts"):
        return

    if context.user_data.get("edit", False):
        if not await check_user(update, context, "contacts_mod", send=False):
            context.user_data["edit"] = False

    search = context.user_data.get("search")
    if not search:
        search = ""

    log_action(update.effective_user, "contacts", search, page)

    searched_contacts = search_contacts(UsersDb.get_users(), search)
    if not context.user_data.get("edit", False):
        searched_contacts = filter_contacts(searched_contacts, REQUIRED_FIELDS)

    text = await create_contacts(searched_contacts, context.bot, update, page)

    if delete:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=keyboards.contacts(searched_contacts, context.user_data.get("edit", False), update, page),
        parse_mode=PARSE_MODE,
    )


async def contacts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["search"] = None
    await contacts(update, context)


async def contacts_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await contacts(update, context, delete=True, page=int(update.callback_query.data.split(" ")[1]))


async def contacts_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context, "contacts_mod", send=False):
        context.user_data["edit"] = False
        await contacts(update, context, delete=True)
        return

    first_field = "name" if not REQUIRED_FIELDS else REQUIRED_FIELDS[0]

    context.user_data["state"] = State[first_field.upper()].name
    context.user_data["user"] = FIELDS.copy()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_" + first_field, update),
        reply_markup=keyboards.cancel(update),
        parse_mode=PARSE_MODE,
    )

    await update.callback_query.answer(
        text=Languages.msg("answer_sent", update),
    )


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: Optional[ObjectId] = None) -> None:
    if not await check_user(update, context, "contacts"):
        return

    if context.user_data.get("edit", False):
        if not await check_user(update, context, "contacts_mod", send=False):
            context.user_data["edit"] = False

    if update.callback_query and update.callback_query.data.startswith("user_edit") and await check_user(update, context, "contacts_mod", send=False):
        context.user_data["edit"] = True

    if not user_id:
        user_id = ObjectId(update.callback_query.data.split(" ")[1])
    user_obj = UsersDb.get_user(user_id)
    if not user_obj:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id,
        )
        await contacts(update, context)
        return

    log_action(update.effective_user, "contact", user_obj["name"])

    await delete_messages(update, context)

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=await user_info(user_obj, update, context.bot),
        reply_markup=keyboards.user(user_obj, user_obj["tg_id"] != update.effective_user.id, update) if context.user_data.get("edit", False) else keyboards.report(user_obj, update),
        parse_mode=PARSE_MODE,
    )
    context.user_data["delete_message_ids"].append(message.message_id)

    if update.callback_query:
        await update.callback_query.answer(
            text=Languages.msg("answer_sent", update),
        )


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id,
    )

    if not await check_user(update, context, "contacts"):
        return

    user_id = ObjectId(update.callback_query.data.split(" ")[1])
    user_obj = UsersDb.get_user(user_id)
    if not user_obj:
        await contacts(update, context)
        return

    log_action(update.effective_user, "report", user_obj["name"])

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_report", update),
        reply_markup=keyboards.cancel(update),
        parse_mode=PARSE_MODE,
    )

    context.user_data["state"] = State.REPORT.name
    context.user_data["user_id"] = user_id

    if update.callback_query:
        await update.callback_query.answer(
            text=Languages.msg("answer_sent", update),
        )


async def report_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id,
    )

    if not await check_user(update, context, "report", send=False):
        return

    report_obj = ReportsDb.get_report(ObjectId(update.callback_query.data.split(" ")[1]))
    if not report_obj or report_obj["is_closed"]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("report_closed", update),
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=PARSE_MODE,
        )
        return

    context.user_data["state"] = State.REPORT_FEEDBACK.name
    context.user_data["report_id"] = report_obj["_id"]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_feedback", update),
        reply_markup=keyboards.cancel(update),
        parse_mode=PARSE_MODE,
    )

    if update.callback_query:
        await update.callback_query.answer(
            text=Languages.msg("answer_sent", update),
        )


async def edit_contact_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context, "contacts_mod", send=False):
        context.user_data["edit"] = False
        await contact(update, context)
        return

    context.user_data["state"] = State.EDIT_NAME.name
    context.user_data["user_id"] = ObjectId(update.callback_query.data.split(" ")[1])

    is_required = "name" in REQUIRED_FIELDS

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_name", update),
        reply_markup=keyboards.cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )
    if not context.user_data.get("delete_message_ids"):
        context.user_data["delete_message_ids"] = []
    context.user_data["delete_message_ids"].append(message.message_id)


async def edit_supervisor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["user_id"] = ObjectId(update.callback_query.data.split(" ")[1])
    context.user_data["search"] = None
    await supervisors(update, context, delete=True)


async def supervisors(update: Update, context: ContextTypes.DEFAULT_TYPE, delete: bool = False, page: int = 1) -> None:
    context.user_data["state"] = State.EDIT_SUPERVISOR.name

    if not await check_user(update, context, "contacts_mod", send=False) or not context.user_data.get("edit", False):
        context.user_data["edit"] = False
        await contact(update, context)
        return

    if not context.user_data.get("user_id"):
        await contacts(update, context)
        return

    search = context.user_data.get("search")
    if not search:
        search = ""

    searched_contacts = search_contacts(UsersDb.get_users(), search)
    text = await create_contacts(searched_contacts, context.bot, update, page, which="supervisors")

    if delete:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=keyboards.contacts(searched_contacts, False, update, page, which="supervisors", user_id=context.user_data.get("user_id")),
        parse_mode=PARSE_MODE,
    )
    if not context.user_data.get("delete_message_ids"):
        context.user_data["delete_message_ids"] = []
    context.user_data["delete_message_ids"].append(message.message_id)


async def supervisors_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await supervisors(update, context, delete=True, page=int(update.callback_query.data.split(" ")[1]))


async def supervisor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["state"] = State.CONTACTS.name
    if not await check_user(update, context, "contacts_mod", send=False):
        context.user_data["edit"] = False
        await contact(update, context)
        return

    if not context.user_data.get("user_id"):
        await contacts(update, context)
        return

    user_id = ObjectId(update.callback_query.data.split(" ")[1])
    UsersDb.edit_user(context.user_data["user_id"], {"supervisor": user_id})

    await contact(update, context, user_id=context.user_data["user_id"])


async def edit_job_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context, "contacts_mod", send=False):
        context.user_data["edit"] = False
        await contact(update, context)
        return

    context.user_data["state"] = State.EDIT_JOB.name
    context.user_data["user_id"] = ObjectId(update.callback_query.data.split(" ")[1])

    is_required = "job_title" in REQUIRED_FIELDS

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_job_title", update),
        reply_markup=keyboards.cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )
    if not context.user_data.get("delete_message_ids"):
        context.user_data["delete_message_ids"] = []
    context.user_data["delete_message_ids"].append(message.message_id)


async def edit_unit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context, "contacts_mod", send=False):
        context.user_data["edit"] = False
        await contact(update, context)
        return

    context.user_data["state"] = State.EDIT_UNIT.name
    context.user_data["user_id"] = ObjectId(
        update.callback_query.data.split(" ")[1])

    is_required = "unit" in REQUIRED_FIELDS

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_unit", update),
        reply_markup=keyboards.cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )
    if not context.user_data.get("delete_message_ids"):
        context.user_data["delete_message_ids"] = []
    context.user_data["delete_message_ids"].append(message.message_id)


async def edit_place(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context, "contacts_mod", send=False):
        context.user_data["edit"] = False
        await contact(update, context)
        return

    context.user_data["state"] = State.EDIT_PLACE.name
    context.user_data["user_id"] = ObjectId(
        update.callback_query.data.split(" ")[1])

    is_required = "place" in REQUIRED_FIELDS

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_place", update),
        reply_markup=keyboards.cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )
    if not context.user_data.get("delete_message_ids"):
        context.user_data["delete_message_ids"] = []
    context.user_data["delete_message_ids"].append(message.message_id)


async def edit_personal_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context, "contacts_mod", send=False):
        context.user_data["edit"] = False
        await contact(update, context)
        return

    context.user_data["state"] = State.EDIT_PERSONAL_PHONE.name
    context.user_data["user_id"] = ObjectId(
        update.callback_query.data.split(" ")[1])

    is_required = "personal_phone" in REQUIRED_FIELDS

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_personal_phone", update),
        reply_markup=keyboards.cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )
    if not context.user_data.get("delete_message_ids"):
        context.user_data["delete_message_ids"] = []
    context.user_data["delete_message_ids"].append(message.message_id)


async def edit_work_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context, "contacts_mod", send=False):
        context.user_data["edit"] = False
        await contact(update, context)
        return

    context.user_data["state"] = State.EDIT_WORK_PHONE.name
    context.user_data["user_id"] = ObjectId(
        update.callback_query.data.split(" ")[1])

    is_required = "work_phone" in REQUIRED_FIELDS

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_work_phone", update),
        reply_markup=keyboards.cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )
    if not context.user_data.get("delete_message_ids"):
        context.user_data["delete_message_ids"] = []
    context.user_data["delete_message_ids"].append(message.message_id)


async def edit_additional_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context, "contacts_mod", send=False):
        context.user_data["edit"] = False
        await contact(update, context)
        return

    context.user_data["state"] = State.EDIT_ADDITIONAL_NUMBER.name
    context.user_data["user_id"] = ObjectId(
        update.callback_query.data.split(" ")[1])

    is_required = "additional_number" in REQUIRED_FIELDS

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_additional_number", update),
        reply_markup=keyboards.cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )
    if not context.user_data.get("delete_message_ids"):
        context.user_data["delete_message_ids"] = []
    context.user_data["delete_message_ids"].append(message.message_id)


async def edit_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context, "contacts_mod", send=False):
        context.user_data["edit"] = False
        await contact(update, context)
        return

    context.user_data["state"] = State.EDIT_EMAIL.name
    context.user_data["user_id"] = ObjectId(
        update.callback_query.data.split(" ")[1])

    is_required = "email" in REQUIRED_FIELDS

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_email", update),
        reply_markup=keyboards.cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )
    if not context.user_data.get("delete_message_ids"):
        context.user_data["delete_message_ids"] = []
    context.user_data["delete_message_ids"].append(message.message_id)


async def user_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context, "contacts_mod", send=False):
        context.user_data["edit"] = False
        await contact(update, context)
        return

    user_id = ObjectId(update.callback_query.data.split(" ")[1])

    user_obj = UsersDb.get_user(user_id)
    if not user_obj:
        await contacts(update, context, delete=True)
        return

    if any([access in user_obj["access"] for access in ADMIN_ACCESS]):
        UsersDb.edit_user(user_id, {"access": USER_ACCESS})
    else:
        UsersDb.edit_user(user_id, {"access": USER_ACCESS + ADMIN_ACCESS})

    await contact(update, context)


async def user_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context, "contacts_mod", send=False):
        context.user_data["edit"] = False
        await contact(update, context)
        return

    user_id = ObjectId(update.callback_query.data.split(" ")[1])

    user_obj = UsersDb.get_user(user_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("user_confirm_delete", update),
        reply_markup=keyboards.confirm_delete(update, user_obj),
        parse_mode=PARSE_MODE,
    )
    await update.callback_query.answer(
        text=Languages.msg("answer_sent", update),
    )


async def user_confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get("delete_message_ids"):
        context.user_data["delete_message_ids"] = []
    context.user_data["delete_message_ids"].append(update.effective_message.message_id)
    await delete_messages(update, context)

    if not await check_user(update, context, "contacts_mod", send=False):
        context.user_data["edit"] = False
        await contact(update, context)
        return

    user_id = ObjectId(update.callback_query.data.split(" ")[1])

    UsersDb.delete_user(user_id)


async def user_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await delete_messages(update, context)

    if not await check_user(update, context, "contacts_mod", send=False):
        context.user_data["edit"] = False


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (context.user_data.get("state") in [State.ADD_QUESTION.name, State.EDIT_QUESTION.name, State.ADD_ANSWER.name, State.EDIT_ANSWER.name] and
            update.message.text == Languages.btn("cancel", update)):
        context.user_data["question"] = None
        context.user_data["state"] = State.FAQ.name

        question_id = context.user_data.get("question_id")
        context.user_data["question_id"] = None

        if context.user_data.get("state") in [State.ADD_QUESTION.name, State.ADD_ANSWER.name]:
            await faq(update, context)
        else:
            if not context.user_data.get("delete_message_ids"):
                context.user_data["delete_message_ids"] = []
            context.user_data["delete_message_ids"].append(update.effective_message.message_id)

            await faq_ans(update, context, question_id=question_id)
        return

    if (context.user_data.get("state") in [State.NAME.name, State.JOB_TITLE.name, State.UNIT.name, State.PLACE.name,
                                           State.PERSONAL_PHONE.name, State.WORK_PHONE.name, State.ADDITIONAL_NUMBER.name, State.EMAIL.name] and
            update.message.text == Languages.btn("cancel", update)):
        context.user_data["user"] = None
        context.user_data["search"] = None
        context.user_data["state"] = State.IDLE.name

        if await check_user(update, context, "contacts_mod", send=False):
            context.user_data["state"] = State.CONTACTS.name
            await contacts(update, context)
        return

    if (context.user_data.get("state") in [State.EDIT_NAME.name, State.EDIT_JOB.name, State.EDIT_UNIT.name, State.EDIT_PLACE.name,
                                           State.EDIT_PERSONAL_PHONE.name, State.EDIT_WORK_PHONE.name, State.EDIT_ADDITIONAL_NUMBER.name, State.EDIT_EMAIL.name] and
            update.message.text == Languages.btn("cancel", update)):
        context.user_data["search"] = None
        context.user_data["state"] = State.CONTACTS.name

        user_id = context.user_data.get("user_id")
        context.user_data["user_id"] = None

        if not context.user_data.get("delete_message_ids"):
            context.user_data["delete_message_ids"] = []
        context.user_data["delete_message_ids"].append(update.effective_message.message_id)

        await contact(update, context, user_id=user_id)
        return

    if context.user_data.get("state") == State.REPORT.name:
        context.user_data["state"] = State.CONTACTS.name

        user_id = context.user_data.get("user_id")
        context.user_data["user_id"] = None

        if user_id:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("report_sent", update),
                reply_markup=ReplyKeyboardRemove(),
                parse_mode=PARSE_MODE
            )
            await contact(update, context, user_id=user_id)
        else:
            return await contacts(update, context)

        if update.message.text == Languages.btn("cancel", update):
            return

        user_obj = UsersDb.get_user(user_id)
        if not user_obj:
            return

        effective_user = UsersDb.get_user_by_tg(update.effective_user.id)
        if not effective_user:
            return

        log_action(update.effective_user, "report_text", user_obj["name"], update.message.text)

        report_id = ReportsDb.add_report({
            "from": effective_user["_id"],
            "user": user_obj["_id"],
            "message": update.message.text,
            "is_closed": False,
        })
        if not report_id:
            return

        report_obj = ReportsDb.get_report(report_id)
        if not report_obj:
            return

        for admin in UsersDb.get_users_by_access("report"):
            try:
                if admin["tg_id"] == 0:
                    continue

                await context.bot.send_message(
                    chat_id=admin["tg_id"],
                    text=Languages.msg("report", update).format(
                        who=effective_user["name"],
                        user=user_obj["name"],
                        report=update.message.text,
                    ),
                    reply_markup=keyboards.report_actions(report_obj, update),
                    parse_mode=PARSE_MODE,
                )
            except Exception as e:
                print(e)

        return

    if context.user_data.get("state") == State.REPORT_FEEDBACK.name:
        context.user_data["state"] = State.CONTACTS.name

        report_id = context.user_data.get("report_id")
        context.user_data["report_id"] = None

        if not report_id:
            return

        report_obj = ReportsDb.get_report(report_id)
        if not report_obj:
            return

        if update.message.text == Languages.btn("cancel", update):
            who = UsersDb.get_user(report_obj["from"])
            user = UsersDb.get_user(report_obj["user"])
            if not who or not user:
                return
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("report", update).format(
                    who=who["name"],
                    user=user["name"],
                    report=report_obj["message"],
                ),
                reply_markup=keyboards.report_actions(report_obj, update),
                parse_mode=PARSE_MODE,
            )
            return

        user_obj = UsersDb.get_user(report_obj["from"])
        await context.bot.send_message(
            chat_id=user_obj["tg_id"],
            text=Languages.msg("feedback", update).format(
                feedback=update.message.text,
            ),
            reply_markup=keyboards.report_feedback(report_obj, update),
            parse_mode=PARSE_MODE,
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("feedback_sent", update),
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=PARSE_MODE,
        )

        ReportsDb.edit_report(report_id, {"is_closed": True})

        return

    effective_user = UsersDb.get_user_by_tg(update.effective_user.id)
    if await check_user(update, context, "faq_mod", send=False) and await check_user(update, context, "contacts_mod", send=False):
        if context.user_data.get("state") in [State.ADD_QUESTION.name, State.EDIT_QUESTION.name]:
            question = update.message.text
            if question is None or question.strip() == "":
                message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=Languages.msg("invalid_question", update),
                    parse_mode=PARSE_MODE,
                )

                if not context.user_data.get("delete_message_ids"):
                    context.user_data["delete_message_ids"] = []
                context.user_data["delete_message_ids"].extend([
                    update.effective_message.message_id,
                    message.message_id
                ])

                await faq_add(update, context)
                return

            context.user_data["state"] = State(State[context.user_data["state"]].value + 1).name
            context.user_data["question"] = {
                "question": question,
                "answers": [],
            }
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("send_answer", update),
                reply_markup=keyboards.cancel(update),
                parse_mode=PARSE_MODE,
            )

            if context.user_data.get("state") == State.EDIT_QUESTION.name:
                if not context.user_data.get("delete_message_ids"):
                    context.user_data["delete_message_ids"] = []
                context.user_data["delete_message_ids"].extend([
                    update.effective_message.message_id,
                    message.message_id
                ])

            return
        elif context.user_data.get("state") in [State.ADD_ANSWER.name, State.EDIT_ANSWER.name]:
            question = context.user_data.get("question")
            if question is None:
                context.user_data["search"] = None
                await faq(update, context, delete=True)
                return

            if update.message.text == Languages.btn("stop_answer", update):
                if not context.user_data.get("delete_message_ids"):
                    context.user_data["delete_message_ids"] = []
                context.user_data["delete_message_ids"].append(update.effective_message.message_id)

                answers = question.get("answers", [])
                if not answers:
                    context.user_data["question"] = None
                    context.user_data["search"] = None
                    await faq(update, context)
                    return
                if context.user_data["state"] == State.ADD_ANSWER.name:
                    FaqDb.add_question(question["question"], answers)
                    text = Languages.msg("question_added", update)
                else:
                    if context.user_data.get("question_id") is None:
                        await faq(update, context, delete=True)
                        return
                    FaqDb.edit_question(context.user_data["question_id"], question["question"], answers)
                    text = Languages.msg("question_edited", update)

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    reply_markup=ReplyKeyboardRemove(),
                    parse_mode=PARSE_MODE,
                )

                await faq(update, context)
                return

            chat_id = update.effective_chat.id
            message_id = update.effective_message.message_id

            # Сохраняем текст сообщения или подпись, если они есть
            message_content = update.effective_message.text or update.effective_message.caption or ""
            context.user_data["question"]["answers"].append({
                "chat_id": chat_id, 
                "message_id": message_id,
                "text": message_content
            })

            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("send_next_answer", update),
                reply_markup=keyboards.stop_answer(update),
                parse_mode=PARSE_MODE,
            )

            if not context.user_data.get("delete_message_ids"):
                context.user_data["delete_message_ids"] = []
            context.user_data["delete_message_ids"].append(message.message_id)

            return
        elif context.user_data.get("state") in [State.EDIT_NAME.name, State.EDIT_JOB.name, State.EDIT_UNIT.name, State.EDIT_PLACE.name,
                                            State.EDIT_PERSONAL_PHONE.name, State.EDIT_WORK_PHONE.name, State.EDIT_ADDITIONAL_NUMBER.name, State.EDIT_EMAIL.name]:
            if not context.user_data.get("delete_message_ids"):
                context.user_data["delete_message_ids"] = []
            context.user_data["delete_message_ids"].append(update.effective_message.message_id)

            user_id = context.user_data.get("user_id")
            if user_id is None:
                await contacts(update, context)
                return
            if context.user_data["state"] == State.EDIT_NAME.name:
                if "name" not in REQUIRED_FIELDS and update.message.text.strip() == Languages.btn("reset", update):
                    UsersDb.edit_user(user_id, {"name": FIELDS["name"]})
                else:
                    UsersDb.edit_user(user_id, {"name": update.message.text})
            elif context.user_data["state"] == State.EDIT_JOB.name:
                if "job_title" not in REQUIRED_FIELDS and update.message.text.strip() == Languages.btn("reset", update):
                    UsersDb.edit_user(user_id, {"job_title": FIELDS["job_title"]})
                else:
                    UsersDb.edit_user(user_id, {"job_title": update.message.text})
            elif context.user_data["state"] == State.EDIT_UNIT.name:
                if "unit" not in REQUIRED_FIELDS and update.message.text.strip() == Languages.btn("reset", update):
                    UsersDb.edit_user(user_id, {"unit": FIELDS["unit"]})
                else:
                    UsersDb.edit_user(user_id, {"unit": update.message.text})
            elif context.user_data["state"] == State.EDIT_PLACE.name:
                if "place" not in REQUIRED_FIELDS and update.message.text.strip() == Languages.btn("reset", update):
                    UsersDb.edit_user(user_id, {"place": FIELDS["place"]})
                else:
                    UsersDb.edit_user(user_id, {"place": update.message.text})
            elif context.user_data["state"] == State.EDIT_ADDITIONAL_NUMBER.name:
                if "additional_number" not in REQUIRED_FIELDS and update.message.text.strip() == Languages.btn("reset", update):
                    UsersDb.edit_user(user_id, {"additional_number": FIELDS["additional_number"]})
                else:
                    if all([c.isdigit() for c in update.message.text]):
                        UsersDb.edit_user(user_id, {"additional_number": int(update.message.text)})
                    else:
                        message1 = await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=Languages.msg("invalid_additional_number", update),
                            parse_mode=PARSE_MODE,
                        )
                        message2 = await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=Languages.msg("send_additional_number", update),
                            reply_markup=keyboards.reset(update) if "additional_number" not in REQUIRED_FIELDS else keyboards.cancel(update),
                        )
                        if not context.user_data.get("delete_message_ids"):
                            context.user_data["delete_message_ids"] = []
                        context.user_data["delete_message_ids"].extend([
                            message1.message_id,
                            message2.message_id,
                        ])
                        return
            elif context.user_data["state"] == State.EDIT_PERSONAL_PHONE.name:
                if "personal_phone" not in REQUIRED_FIELDS and update.message.text.strip() == Languages.btn("reset", update):
                    UsersDb.edit_user(user_id, {"personal_phone": FIELDS["personal_phone"]})
                else:
                    phone = parse_phone(update.message.text)
                    if not phone:
                        message1 = await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=Languages.msg("invalid_personal_phone", update),
                            parse_mode=PARSE_MODE,
                        )
                        message2 = await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=Languages.msg("send_personal_phone", update),
                            reply_markup=keyboards.reset(update) if "phone" not in REQUIRED_FIELDS else keyboards.cancel(update),
                        )
                        if not context.user_data.get("delete_message_ids"):
                            context.user_data["delete_message_ids"] = []
                        context.user_data["delete_message_ids"].extend([
                            message1.message_id,
                            message2.message_id,
                        ])
                        return
                    else:
                        UsersDb.edit_user(user_id, {"personal_phone": phone})
            elif context.user_data["state"] == State.EDIT_WORK_PHONE.name:
                if "work_phone" not in REQUIRED_FIELDS and update.message.text.strip() == Languages.btn("reset", update):
                    UsersDb.edit_user(user_id, {"work_phone": FIELDS["work_phone"]})
                else:
                    phone = parse_phone(update.message.text)
                    if not phone:
                        message1 = await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=Languages.msg("invalid_work_phone", update),
                            parse_mode=PARSE_MODE,
                        )
                        message2 = await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=Languages.msg("send_work_phone", update),
                            reply_markup=keyboards.reset(update) if "phone" not in REQUIRED_FIELDS else keyboards.cancel(update),
                        )
                        if not context.user_data.get("delete_message_ids"):
                            context.user_data["delete_message_ids"] = []
                        context.user_data["delete_message_ids"].extend([
                            message1.message_id,
                            message2.message_id,
                        ])
                        return
                    else:
                        UsersDb.edit_user(user_id, {"work_phone": phone})
            elif context.user_data["state"] == State.EDIT_EMAIL.name:
                if "email" not in REQUIRED_FIELDS and update.message.text.strip() == Languages.btn("reset", update):
                    UsersDb.edit_user(user_id, {"email": FIELDS["email"]})
                elif not await check_email(update.message.text):
                    message1 = await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=Languages.msg("invalid_email", update),
                        parse_mode=PARSE_MODE,
                    )
                    message2 = await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=Languages.msg("send_email", update),
                        reply_markup=keyboards.reset(update) if "email" not in REQUIRED_FIELDS else keyboards.cancel(update),
                    )
                    if not context.user_data.get("delete_message_ids"):
                        context.user_data["delete_message_ids"] = []
                    context.user_data["delete_message_ids"].extend([
                        message1.message_id,
                        message2.message_id,
                    ])
                    return
                else:
                    UsersDb.edit_user(user_id, {"email": update.message.text})
            context.user_data["state"] = State.CONTACTS.name
            await contact(update, context, user_id=user_id)
            return

    if context.user_data.get("state", None) in [State.NAME.name, State.JOB_TITLE.name, State.UNIT.name, State.PLACE.name,
                                                State.PERSONAL_PHONE.name, State.WORK_PHONE.name, State.ADDITIONAL_NUMBER.name, State.EMAIL.name]:
        if update.message.text == Languages.btn("cancel", update):
            context.user_data["user"] = None
            if await check_user(update, context, "contacts_mod", send=False):
                context.user_data["state"] = State.CONTACTS.name
                await contacts(update, context)
            elif await check_user(update, context, "contacts", send=False):
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=Languages.msg("dont_understand", update),
                    parse_mode=PARSE_MODE,
                )
            return

        field = State[context.user_data["state"]].name.lower()
        if (update.message.text is None or update.message.text.strip() == "" or
                context.user_data.get("state", None) in [State.PERSONAL_PHONE.name, State.WORK_PHONE.name] and not parse_phone(update.message.text) or
                context.user_data.get("state", None) == State.ADDITIONAL_NUMBER.name and not all([c.isdigit() for c in update.message.text]) or
                context.user_data.get("state", None) == State.EMAIL.name and not await check_email(update.message.text)):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("invalid_" + field, update),
                parse_mode=PARSE_MODE,
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("send_" + field, update),
                reply_markup=keyboards.cancel(update),
                parse_mode=PARSE_MODE,
            )
            return
        else:
            if context.user_data.get("user") is None:
                context.user_data["user"] = FIELDS.copy()
            
            log_action(update.effective_user, "register", field, update.message.text)

            context.user_data["user"][field] = parse_phone(update.message.text) if context.user_data.get("state", None) in [State.PERSONAL_PHONE.name, State.WORK_PHONE.name] else update.message.text
            start_search = False
            next_field: Optional[str] = None
            for fld in REQUIRED_FIELDS:
                if fld == field:
                    start_search = True
                elif start_search and fld in REQUIRED_FIELDS:
                    next_field = fld
                    break
            if next_field is not None:
                context.user_data["state"] = State[next_field.upper()].name
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=Languages.msg("send_" + next_field, update),
                    reply_markup=keyboards.cancel(update),
                    parse_mode=PARSE_MODE,
                )
                return

            fields = {
                fld: context.user_data["user"].get(fld, "") for fld in REQUIRED_FIELDS
            }
            for fld in fields:
                if fields[fld] == "" and fld in REQUIRED_FIELDS:
                    if await check_user(update, context, "contacts_mod", send=False):
                        context.user_data["state"] = State.CONTACTS.name
                        await contacts(update, context)
                        return
                    elif await check_user(update, context, "contacts", send=False):
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=Languages.msg("dont_understand", update),
                            parse_mode=PARSE_MODE,
                        )
                        return

            if not await check_user(update, context, "contacts_mod", send=False):
                context.user_data["user"].update({
                    "tg_id": update.effective_user.id,
                    "access": [],
                })

            user_id = UsersDb.add_user(context.user_data["user"])
            user_obj = UsersDb.get_user(user_id)

            if await check_user(update, context, "contacts_mod", send=False):
                await contact(update, context, user_id=user_id)
                return

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("not_user_request", update),
                parse_mode=PARSE_MODE,
            )

            for admin in UsersDb.get_users_by_access("request"):
                try:
                    if admin["tg_id"] == 0:
                        continue

                    await context.bot.send_message(
                        chat_id=admin["tg_id"],
                        text=Languages.msg("request_user", update).format(data=await user_info(user_obj, update, context.bot)),
                        reply_markup=keyboards.accept_deny(user_id),
                        parse_mode=PARSE_MODE,
                    )
                except:
                    pass

            return

    context.user_data["search"] = update.message.text if update.message.text else ""
    if not context.user_data.get("state"):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("dont_understand", update),
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=PARSE_MODE,
        )
    elif context.user_data["state"] == State.FAQ.name:
        await faq(update, context)
    elif context.user_data["state"] == State.CONTACTS.name:
        await contacts(update, context)
    elif context.user_data["state"] == State.EDIT_SUPERVISOR.name:
        await supervisors(update, context)
    else:
        await contacts(update, context)
