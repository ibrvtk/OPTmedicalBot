import aiosqlite



async def create():
    async with aiosqlite.connect('databases/blacklist.db') as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS blacklist (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT
            )
        """)
        await db.commit()


async def addProduct(user_id: str):
    async with aiosqlite.connect('databases/blacklist.db') as db:
        await db.execute("""
            INSERT INTO blacklist (user_id)
            VALUES (?)
        """, (user_id))
        await db.commit()


async def deleteProduct(user_id: int):
    async with aiosqlite.connect('databases/blacklist.db') as db:
        await db.execute("DELETE FROM blacklist WHERE user_id = ?", (user_id,))
        await db.commit()