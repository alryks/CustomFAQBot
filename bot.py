import traceback

from typing import Optional

from telegram.ext import ApplicationBuilder, Application

from lang import Languages


class Bot:
    def __init__(self, token: str) -> None:
        self.token = token
        self.handlers = []
        self.commands = []
        self.app: Optional[Application] = None

    async def run(self, start_command: bool = False) -> bool:
        try:
            self.app = ApplicationBuilder().token(self.token).build()
            self.app.add_handlers(self.handlers)
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()

            if start_command:
                self.commands.append("start")

            for lang in Languages.langs:
                commands = []
                for command in self.commands:
                    commands.append((command, Languages.cmd(command, lang)))
                await self.app.bot.set_my_commands(commands=commands, language_code=lang)

            return True
        except:
            # traceback.print_exc()
            return False

    async def stop(self) -> bool:
        result: bool = True
        try:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
        except:
            # traceback.print_exc()
            result = False
        self.app = None
        return result