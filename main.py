import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from data.config import token

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level=logging.INFO)

bot = Bot(token=token, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
scheduler = AsyncIOScheduler(timezone='Europe/Kyiv')


if __name__ == '__main__':
    from handlers.user_handlers import dp, on_startup, on_shutdown
    loop = asyncio.get_event_loop()
    executor.start_polling(dp, loop=loop, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)