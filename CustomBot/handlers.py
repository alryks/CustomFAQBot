from telegram import Update, User, ReplyKeyboardRemove
from telegram.ext import ContextTypes

import inspect

from . import keyboards
from keyboards import cancel

from db import BotsDb

from state import State

from misc import create_faq


async def run_faq(update: Update, context: ContextTypes.DEFAULT_TYPE, edit=False, delete=False) -> None:
    context.user_data["state"] = State.IDLE.name

    bot_obj = BotsDb.get_bot_by_id(context.bot.id)
    if bot_obj is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="This bot is not registered in our system.",
        )
        return
    bot_faq = bot_obj["faq"]
    text = create_faq(bot_faq, context.bot.bot.username, context.bot.bot.full_name)

    if delete:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode="HTML",
        reply_markup=keyboards.faq(bot_obj, edit),
    )


async def edit_faq(update: Update, context: ContextTypes.DEFAULT_TYPE, delete=True) -> None:
    await run_faq(update, context, edit=True, delete=delete)


async def faq_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Send question:",
        reply_markup=cancel()
    )

    context.user_data["state"] = State.QUESTION.name


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = context.user_data.get("state")
    if state == State.QUESTION.name:
        if update.message.text != "✖️Cancel":
            question = update.message.text
            if question is None or question.strip() == "":
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Invalid question!"
                )
                await faq_add(update, context)
                return
            else:
                context.user_data["state"] = State.ANSWER.name

                context.user_data["question"] = question

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Send answer:",
                    reply_markup=cancel()
                )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Operation canceled!",
                reply_markup=ReplyKeyboardRemove()
            )

            await edit_faq(update, context)
    elif state == State.ANSWER.name:
        delete = True
        if update.message.text != "✖️Cancel":
            bot_obj = BotsDb.get_bot_by_id(context.bot.id)
            if bot_obj is None:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="This bot is not registered in our system.",
                )
                return
            question = context.user_data.get("question")
            if question is None:
                await edit_faq(update, context, delete=delete)

            chat_id = update.effective_chat.id
            message_id = update.effective_message.message_id

            context.user_data["state"] = State.IDLE.name

            BotsDb.add_faq(bot_obj["_id"], question, chat_id, message_id)

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Question added!",
                reply_markup=ReplyKeyboardRemove()
            )
            delete = False
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Operation canceled!",
                reply_markup=ReplyKeyboardRemove()
            )

        await edit_faq(update, context, delete=delete)
    else:
        context.user_data["state"] = State.IDLE.name
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="I don't understand you!",
        )


async def faq_ans(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot_obj = BotsDb.get_bot_by_id(context.bot.id)
    if bot_obj is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="This bot is not registered in our system.",
        )
        return
    number = int(update.callback_query.data.split(" ")[2])
    bot_faq = bot_obj["faq"]
    if number >= len(bot_faq):
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.callback_query.message.message_id,
        )
        await run_faq(update, context)
        await update.callback_query.answer(
            text="Question not found.",
        )
        return
    answer = bot_obj["faq"][number]["answer"]
    chat_id = answer["chat_id"]
    message_id = answer["message_id"]

    delete_message_id = context.user_data.get("delete_message_id")
    if delete_message_id is not None:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=delete_message_id
        )

    context.user_data["delete_message_id"] = (await context.bot.copy_message(
        chat_id=update.effective_chat.id,
        from_chat_id=chat_id,
        message_id=message_id
    )).message_id
    await update.callback_query.answer(
        text="Answer sent.",
    )


async def faq_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )