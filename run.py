from config import bot

from app.handlers import handlers
from app.callbacks import callbacks
from app.scheduler import scheduler

import databases.assortment as dba
import databases.posts as dbp

import asyncio

from aiogram import Dispatcher


dp = Dispatcher()



async def main():
    dp.include_router(handlers)
    dp.include_router(callbacks)

    await dba.create()
    await dbp.create()

    asyncio.create_task(scheduler(bot))
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        print("✅")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("💤")
    except Exception as e:
        print(f"❗ {e}")