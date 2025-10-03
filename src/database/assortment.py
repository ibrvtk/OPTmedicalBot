import aiosqlite



async def create():
    async with aiosqlite.connect('databases/assortment.db') as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS assortment (
                number INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                price INTEGER,
                priceDiscount INTEGER
            )
        """)
        await db.commit()


async def add(name: str, description: str, price: int, priceDiscount: int):
    async with aiosqlite.connect('databases/assortment.db') as db:
        cursor = await db.execute("""
            INSERT INTO assortment (name, description, price, priceDiscount)
            VALUES (?, ?, ?, ?)
        """, (name, description, price, priceDiscount))
        await db.commit()
        product_number = cursor.lastrowid
        return product_number


async def delete(number: int):
    async with aiosqlite.connect('databases/assortment.db') as db:
        await db.execute("DELETE FROM assortment WHERE number = ?", (number,))
        await db.commit()