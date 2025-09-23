from config import ADMINCHATS, ADMINUSERS, userData, shopName, shopDescription
import app.keyboards as kb

import aiosqlite

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message


handlers = Router()



@handlers.message(Command("start"), F.chat.type == "private")
async def cmdStart(message: Message):
    userData[message.from_user.id] = {
        'user_id': message.from_user.id,
        'inAssortment': "False",
        'assortmentCart': "None",
        'assortmentCount': 1,
        'assortmentCheque': 0,
        'assortmentChequeGlobal': 0,
    }

    await message.answer(f"🔵 <b><a href='https://t.me/+YvGo7Qxlz2I3MDg6'>OPT MEDICAL</a></b>{shopDescription}",
                            reply_markup=kb.chooseService)


# 📄 Ассортимент
@handlers.message(F.text == "📄 Ассортимент")
async def fAssortment(message: Message):
    userData[message.from_user.id]['inAssortment'] = "True"
    await message.answer(f"{shopName}\nАссортимент магазина и онлайн заказ.",
                         reply_markup=await kb.assortmentProducts())


@handlers.message(F.text == "🛒 Корзина")
async def fAssortmentCart(message: Message):
    if userData[message.from_user.id]['assortmentCart'] == "None":
        await message.reply("🛒 <b>Корзина</b>\n<i>Пусто...</i>")
    else:
        await message.reply(f"🛒 <b>Корзина</b>\n{userData[message.from_user.id]['assortmentCart']}\n"
                            f"<u>Итоговая сумма: {userData[message.from_user.id]['assortmentChequeGlobal']} ₽</u>",
                            reply_markup=kb.cartKeyboard)
        
@handlers.message(F.text.contains("—") & F.text.contains("₽"))
async def fAssortmentProduct(message: Message):
    if userData[message.from_user.id]['inAssortment'] != "True":
        await message.reply("⛔ <b>Сначала закончите действующий заказ!</b>")
        return
    
    productName = message.text.split("—")[0].strip()
    async with aiosqlite.connect('databases/assortment.db') as db:
        async with db.execute("SELECT description, price, priceDiscount FROM assortment WHERE name = ?", (productName,)) as cursor:
            result = await cursor.fetchone()

    productDescription = result[0]
    productPrice = int(result[1])
    productPriceDiscount = int(result[2])
    productPriceDiscounted = productPrice - productPriceDiscount
    
    userData[message.from_user.id]['inAssortment'] = productName
    userData[message.from_user.id]['assortmentCheque'] = userData[message.from_user.id]['assortmentCount'] * productPriceDiscounted

    productPriceDiscountedText = f"{productPrice} ₽" if productPriceDiscount == 0 else f"<s>{productPrice}</s> {productPriceDiscounted} ₽"
    await message.reply(f"<b>{productName}</b>\n{productDescription}\n\n"
                        f"Цена за штуку: {productPriceDiscountedText}\n"
                        f"Кол-во: {userData[message.from_user.id]['assortmentCount']}\n"
                        f"Итоговая цена: {userData[message.from_user.id]['assortmentCheque']} ₽",
                        reply_markup=kb.assortmentPageButtons)


@handlers.message(F.text == "🔙 Назад")
async def fAssortmentBack(message: Message):
    userData[message.from_user.id]['inAssortment'] = "False"
    await message.answer(f"{shopName}{shopDescription}",
                         reply_markup=kb.chooseService)


# Админский раздел
# /assortment
@handlers.message(Command("assortment"), (F.chat.id.in_(ADMINCHATS)) | (F.from_user.id.in_(ADMINUSERS)))
async def amdcmdPost(message: Message):
    await message.answer("Управление ассортиментом.", 
                        reply_markup=kb.assortmentKeyboard)


# /posts
@handlers.message(Command("posts"), (F.chat.id.in_(ADMINCHATS)) | (F.from_user.id.in_(ADMINUSERS)))
async def amdcmdPost(message: Message):
    await message.answer("Управление отложенными постами.", 
                        reply_markup=kb.postsKeyboard)