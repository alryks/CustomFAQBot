from telegram import Update
from telegram.ext import ContextTypes

from bson import ObjectId

from config import BOT

from . import keyboards
from keyboards import cancel

from db import BotsDb

from .state import State

from misc import create_faq, filter_faq


async def check_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if BotsDb.is_user(BotsDb.get_bot_by_id(context.bot.id)["_id"], update.effective_user.id):
        return True

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="You are not bot user! Requesting access...",
    )

    name = update.effective_user.full_name + (f" @{update.effective_user.username}" if update.effective_user.username else "")
    bot_obj = BotsDb.get_bot_by_id(context.bot.id)

    for admin in bot_obj["admins"]:
        await BOT.app.bot.send_message(
            chat_id=admin,
            text=f"User <b>{name}</b> requested access to @{context.bot.bot.username}",
            parse_mode="HTML",
            reply_markup=keyboards.accept_deny(bot_obj, update.effective_user.id)
        )

    return False


async def check_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"], update.effective_user.id):
        return True

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="You are not bot admin! Requesting access...",
    )

    name = update.effective_user.full_name + (f" @{update.effective_user.username}" if update.effective_user.username else "")
    bot_obj = BotsDb.get_bot_by_id(context.bot.id)

    for admin in bot_obj["admins"]:
        await BOT.app.bot.send_message(
            chat_id=admin,
            text=f"User <b>{name}</b> requested <b>admin rights</b> to @{context.bot.bot.username}",
            parse_mode="HTML",
            reply_markup=keyboards.accept_deny(bot_obj, update.effective_user.id, is_admin=True)
        )

    return False


async def run_faq(update: Update, context: ContextTypes.DEFAULT_TYPE, edit=False, delete=False, page=1) -> None:
    context.user_data["state"] = State.IDLE.name

    if not await check_user(update, context):
        return

    search = context.user_data.get("search")
    if search is None:
        search = ""

    bot_faq = filter_faq(BotsDb.get_bot_by_id(context.bot.id)["faq"], search)
    bot_faq = [faq for faq in bot_faq if search.lower() in faq["question"].lower()]

    text = create_faq(bot_faq, context.bot.bot.username, context.bot.bot.full_name, page)

    if delete:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode="HTML",
        reply_markup=keyboards.faq(bot_faq, edit, page),
    )


async def edit_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_admin(update, context):
        return
    await run_faq(update, context, edit=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["search"] = None
    await run_faq(update, context)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (context.user_data.get("state") in [State.ADD_QUESTION.name,
                                           State.EDIT_QUESTION.name,
                                           State.ADD_ANSWER.name,
                                           State.EDIT_ANSWER.name] and
            update.message.text == "✖️Cancel"):
        context.user_data["question"] = None
        context.user_data["answers"] = None
        context.user_data["search"] = None
        context.user_data["state"] = State.IDLE.name
        await edit_faq(update, context)
        return

    if BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"], update.effective_user.id):
        if context.user_data["state"] in [State.ADD_QUESTION.name, State.EDIT_QUESTION.name]:
            question = update.message.text
            if question is None or question.strip() == "":
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Invalid question!"
                )
                await faq_add(update, context)
                return

            context.user_data["state"] = State(State[context.user_data["state"]].value + 1).name
            context.user_data["question"] = question.strip()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Send answer:",
                reply_markup=keyboards.stop_answer()
            )
            context.user_data["answers"] = None
            return
        elif context.user_data["state"] in [State.ADD_ANSWER.name, State.EDIT_ANSWER.name]:
            question = context.user_data.get("question")
            if question is None:
                context.user_data["search"] = None
                await run_faq(update, context, edit=True, delete=True)
                return

            if update.message.text == "🛑Stop answering":
                answers = context.user_data.get("answers")
                if answers is None:
                    context.user_data["question"] = None
                    context.user_data["answers"] = None
                    context.user_data["search"] = None
                    await edit_faq(update, context)
                    return
                bot_obj = BotsDb.get_bot_by_id(context.bot.id)
                if context.user_data["state"] == State.ADD_ANSWER.name:
                    BotsDb.add_question(bot_obj["_id"], question, answers)
                    text = "Question added!"
                else:
                    if context.user_data.get("question_id") is None:
                        await run_faq(update, context, edit=True, delete=True)
                        return
                    BotsDb.edit_question(bot_obj["_id"], context.user_data["question_id"], question, answers)
                    text = "Question edited!"

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                )

                await edit_faq(update, context)
                return

            chat_id = update.effective_chat.id
            message_id = update.effective_message.message_id

            if context.user_data.get("answers") is None:
                context.user_data["answers"] = []

            context.user_data["answers"].append({"chat_id": chat_id, "message_id": message_id})

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Send next answer:",
                reply_markup=keyboards.stop_answer()
            )

            return

    if not await check_user(update, context):
        return

    if context.user_data["state"] != State.IDLE.name:
        context.user_data["state"] = State.IDLE.name

    context.user_data["search"] = update.message.text if update.message.text else ""
    await run_faq(update, context)


async def faq_ans(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context):
        return

    question = BotsDb.get_question(BotsDb.get_bot_by_id(context.bot.id)["_id"], ObjectId(update.callback_query.data.split(" ")[1]))
    if question is None:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.callback_query.message.message_id,
        )
        await run_faq(update, context)
        return
    answers = question["answers"]

    delete_message_ids = context.user_data.get("delete_message_ids")
    if delete_message_ids is not None:
        for delete_message_id in delete_message_ids:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=delete_message_id
            )

    context.user_data["delete_message_ids"] = []
    for answer in answers:
        message = await context.bot.copy_message(
            chat_id=update.effective_chat.id,
            from_chat_id=answer["chat_id"],
            message_id=answer["message_id"],
        )
        context.user_data["delete_message_ids"].append(message.message_id)
    await update.callback_query.answer(
        text="Answer sent.",
    )


async def faq_ans_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await run_faq(update, context, delete=True, page=int(update.callback_query.data.split(" ")[1]))


async def faq_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_admin(update, context):
        return

    bot_obj = BotsDb.get_bot_by_id(context.bot.id)
    question = BotsDb.get_question(bot_obj["_id"], ObjectId(update.callback_query.data.split(" ")[1]))
    if question is None:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        await edit_faq(update, context)
        return

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Current question:\n\n{question['question']}",
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Current answers:",
    )

    for answer in question["answers"]:
        await context.bot.copy_message(
            chat_id=update.effective_chat.id,
            from_chat_id=answer["chat_id"],
            message_id=answer["message_id"],
        )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="What do you want to do with this question?",
        reply_markup=keyboards.faq_edit(question["_id"])
    )


async def faq_edit_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await run_faq(update, context, edit=True, delete=True, page=int(update.callback_query.data.split(" ")[1]))


async def faq_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_admin(update, context):
        return

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Send question:",
        reply_markup=cancel()
    )

    context.user_data["state"] = State.ADD_QUESTION.name


async def faq_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )


async def question_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_admin(update, context):
        return

    context.user_data["question_id"] = ObjectId(update.callback_query.data.split(" ")[1])
    context.user_data["state"] = State.EDIT_QUESTION.name
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Send new question:",
        reply_markup=cancel()
    )


async def question_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_admin(update, context):
        return

    question_id = ObjectId(update.callback_query.data.split(" ")[1])
    bot_obj = BotsDb.get_bot_by_id(context.bot.id)
    BotsDb.delete_question(bot_obj["_id"], question_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Question deleted!",
    )

    await edit_faq(update, context)


async def question_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_admin(update, context):
        return

    await run_faq(update, context, edit=True, delete=True)