from telegram import Update, ReplyKeyboardRemove, User
from telegram.ext import ContextTypes, Application

from bson import ObjectId

from typing import Union

import keyboards

from db import BotsDb

from state import State, bots

from CustomBot.custom_bot import CustomBot

from misc import create_faq


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["state"] = State.IDLE.name

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Your FAQs:",
        reply_markup=keyboards.bots(await BotsDb.get_user_bot_usernames(update.effective_user.id), 1)
    )


async def add_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # delete message, from where this callback was called
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Send token of your bot:",
        reply_markup=keyboards.cancel()
    )

    context.user_data["state"] = State.TOKEN.name


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get("state") != State.TOKEN.name:
        return
    if update.message.text != "✖️Cancel":
        user_bot = CustomBot(update.message.text)
        if not await user_bot.run():
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Incorrect token!"
            )
            await add_bot(update, context)
            return

        bot_id = BotsDb.add_bot(update.message.text, update.effective_user.id)
        if bot_id is None:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Bot already exists!"
            )
            await add_bot(update, context)
            return

        bots[bot_id] = user_bot
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Operation canceled!",
            reply_markup=ReplyKeyboardRemove()
        )

    await start(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["state"] = State.IDLE.name

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer(" ".join(update.callback_query.data.split(" ")[1:]))


async def bot_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await context.bot.edit_message_reply_markup(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id,
            reply_markup=keyboards.bots(await BotsDb.get_user_bot_usernames(update.effective_user.id),
                                       int(update.callback_query.data.split(" ")[1]))
        )
    except:
        await update.callback_query.answer("Page not found!")


async def callback_check_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[tuple[ObjectId, Application], None]:
    bot_id = ObjectId(update.callback_query.data.split(" ")[1])
    if not BotsDb.is_admin(bot_id, update.effective_user.id):
        await update.callback_query.answer("You are not an admin!")
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        await start(update, context)
        return

    if bot_id not in bots:
        await update.callback_query.answer("Bot is not running!")
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        await start(update, context)
        return

    app = bots[bot_id].app
    if app is None:
        bots.pop(bot_id)
        await update.callback_query.answer("Bot is not running!")
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        await start(update, context)
        return

    return bot_id, app


async def context_data_check_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[tuple[ObjectId, Application], None]:
    bot_id = context.user_data.get("bot_id")
    if bot_id is None:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        await start(update, context)
        return

    if not BotsDb.is_admin(bot_id, update.effective_user.id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You are not an admin!"
        )
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        await start(update, context)
        return

    if bot_id not in bots:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Bot is not running!"
        )
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        await start(update, context)
        return

    app = bots[bot_id].app
    if app is None:
        bots.pop(bot_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Bot is not running!"
        )
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        await start(update, context)
        return

    return bot_id, app


async def bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    if update.callback_query is not None:
        data = await callback_check_bot(update, context)
    else:
        data = await context_data_check_bot(update, context)
    if data is None:
        return
    bot_id, app = data

    bot_user: User = await app.bot.get_me()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Your @{bot_user.username}:",
        reply_markup=keyboards.bot(BotsDb.get_bot(bot_id))
    )


async def bot_private(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def bot_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def bot_admins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def bot_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot_id = ObjectId(update.callback_query.data.split(" ")[1])
    BotsDb.delete_bot(bot_id)
    if bot_id in bots:
        await bots[bot_id].stop()
        bots.pop(bot_id)

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    await start(update, context)


async def bot_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    await start(update, context)
