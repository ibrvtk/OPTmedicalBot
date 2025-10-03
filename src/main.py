from config import bot

from app.handlers import handlers
from app.callbacks import callbacks
from app.scheduler import scheduler

import database.assortment as dba
import database.posts as dbp

import asyncio

from aiogram import Dispatcher


dp = Dispatcher()



async def main():
    dp.include_router(handlers)
    dp.include_router(callbacks)

    await dba.create()
    await dbp.create()

    asyncio.create_task(scheduler(bot))

    print("(V) main.py: main(): успех.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"(XXX) main.py: Ошибка при запуске: {e}.")