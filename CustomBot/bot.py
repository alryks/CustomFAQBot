import traceback

from telegram.ext import ApplicationBuilder


class Bot:
    def __init__(self, token: str) -> None:
        self.token = token
        self.handlers = []
        self.app = None

    async def run(self) -> bool:
        try:
            self.app = ApplicationBuilder().token(self.token).build()
            self.app.add_handlers(self.handlers)
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()
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