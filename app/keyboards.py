from config import kayboardPlaceholderChoose

import aiosqlite

from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder



chooseService = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📄 Ассортимент")],
    [KeyboardButton(text="🛒 Корзина")]
],
resize_keyboard=True,
input_field_placeholder=f"{kayboardPlaceholderChoose}")


# 📄 Ассортимент
async def assortmentProducts():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="🔙 Назад"))

    async with aiosqlite.connect('databases/assortment.db') as db:
        async with db.execute("SELECT name, price, priceDiscount FROM assortment") as cursor:
            products = await cursor.fetchall()

    for name, price, priceDiscount in products:
        priceDiscounted = price - priceDiscount
        if priceDiscount == 0:
            assortmentProductButtonText = f"{name} — {price}₽/1шт."
        else:
            assortmentProductButtonText = f"{name} — {priceDiscounted}₽/1шт. 🔥"
        keyboard.add(KeyboardButton(text=f"{assortmentProductButtonText}"))

    return keyboard.adjust(2).as_markup(
        resize_keyboard=True,
        input_field_placeholder=kayboardPlaceholderChoose)

assortmentPageButtons = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛒 В корзину", callback_data="add")],
    [InlineKeyboardButton(text="➕", callback_data="plus"), 
     InlineKeyboardButton(text="➖", callback_data="minus")]
])


cartKeyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📦 Приступить к оформлению", callback_data="cartBuy"),
     InlineKeyboardButton(text="🧹 Очистить корзину", callback_data="cartClear")]
])


# Админский раздел
# /assortment
assortmentKeyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Добавить продукт", callback_data="assortmentAdd"),
     InlineKeyboardButton(text="Список продуктов", callback_data="assortmentList")]
])

async def assortmentList():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="assortmentListBack"))
    
    async with aiosqlite.connect('databases/assortment.db') as db:
        async with db.execute("SELECT number, name FROM assortment") as cursor:
            products = await cursor.fetchall()

    for number, name in products:
        keyboard.add(InlineKeyboardButton(text=f"{name}", callback_data=f"product_{number}"))

    return keyboard.adjust(2).as_markup()

def assortmentListActions_(productNumber: int):
    keyboard = InlineKeyboardBuilder()
    
    keyboard.add(InlineKeyboardButton(text="🔥 Добавить/убрать скидку", callback_data=f"assortmentListActionsNewPriceDiscount_{productNumber}"))
    keyboard.add(InlineKeyboardButton(text="📜 Изменить описание", callback_data=f"assortmentListActionsNewDescription_{productNumber}"))
    keyboard.add(InlineKeyboardButton(text="❌ Удалить", callback_data=f"assortmentListActionsDelete_{productNumber}"))
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="assortmentListActionsBack"))
    
    return keyboard.adjust(3).as_markup()


# /posts
postsKeyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Написать пост", callback_data="postsAdd"),
     InlineKeyboardButton(text="Список постов", callback_data="postsList")]
])

async def postsList():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="postsListBack"))
    
    async with aiosqlite.connect('databases/posts.db') as db:
        async with db.execute("SELECT post_id, text FROM posts") as cursor:
            posts = await cursor.fetchall()

    for post_id, text in posts:
        keyboard.add(InlineKeyboardButton(text=f"{text}", callback_data=f"post_{post_id}"))

    return keyboard.adjust(2).as_markup()

def postsListActions_(postId: int):
    keyboard = InlineKeyboardBuilder()
    
    keyboard.add(InlineKeyboardButton(text="⏰ Изменить время", callback_data=f"postsListActionsNewTime_{postId}"))
    keyboard.add(InlineKeyboardButton(text="📜 Изменить текст", callback_data=f"postsListActionsNewText_{postId}"))
    keyboard.add(InlineKeyboardButton(text="❌ Удалить", callback_data=f"postsActionsDelete_{postId}"))
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="postsListActionsBack"))
    
    return keyboard.adjust(3).as_markup()