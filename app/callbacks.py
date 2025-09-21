from config import CHANNEL, userData
import app.keyboards as kb

import databases.assortment as dba
import databases.posts as dbp

import aiosqlite
from datetime import datetime

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


callbacks = Router()



# 🛒 Ассортимент
@callbacks.callback_query(F.data == "add")
async def cbAdd(callback: CallbackQuery):
    userData[callback.from_user.id]['assortmentChequeGlobal'] += userData[callback.from_user.id]['assortmentCheque']
    result = f"{userData[callback.from_user.id]['inAssortment']} ({userData[callback.from_user.id]['assortmentCount']} шт.) ({userData[callback.from_user.id]['assortmentCheque']} ₽)\n"

    if userData[callback.from_user.id]['assortmentCart'] == "None":
        userData[callback.from_user.id]['assortmentCart'] = result
    else:
        userData[callback.from_user.id]['assortmentCart'] += result

    userData[callback.from_user.id]['assortmentCount'] = 1
    userData[callback.from_user.id]['inAssortment'] = "True"

    await callback.message.edit_text(f"<b>{result}</b> успешно добавлен в корзину!",
                                     reply_markup=None)

@callbacks.callback_query(F.data == "plus")
async def cbPlus(callback: CallbackQuery):
    userData[callback.from_user.id]['assortmentCount'] += 1
    productName = userData[callback.from_user.id]['inAssortment']

    async with aiosqlite.connect('databases/assortment.db') as db:
        async with db.execute("SELECT description, price, priceDiscount FROM assortment WHERE name = ?", (productName,)) as cursor:
            result = await cursor.fetchone()

    if result:
        productDescription = result[0]
        productPrice = int(result[1])
        productPriceDiscount = int(result[2])
        productPriceDiscounted = productPrice - productPriceDiscount
        userData[callback.from_user.id]['assortmentCheque'] = userData[callback.from_user.id]['assortmentCount'] * productPriceDiscounted
        

    productPriceDiscountedText = f"{productPrice} ₽" if productPriceDiscount == 0 else f"<s>{productPrice}</s> {productPriceDiscounted} ₽"
    await callback.message.edit_text(f"<b>{productName}</b>\n{productDescription}\n\n"
                        f"Цена за штуку: {productPriceDiscountedText}\n"
                        f"Кол-во: {userData[callback.from_user.id]['assortmentCount']}\n"
                        f"Итоговая цена: {userData[callback.from_user.id]['assortmentCheque']} ₽",
                        reply_markup=kb.assortmentPageButtons)
        
@callbacks.callback_query(F.data == "minus")
async def cbMinus(callback: CallbackQuery):
    userData[callback.from_user.id]['assortmentCount'] -= 1
    
    if userData[callback.from_user.id]['assortmentCount'] == 0:
        await callback.message.edit_text(f"❌ Заказ товара <b>{userData[callback.from_user.id]['inAssortment']}</b> отменён.")
        userData[callback.from_user.id]['assortmentCount'] = 1
        userData[callback.from_user.id]['inAssortment'] = "True"
    else:
        productName = userData[callback.from_user.id]['inAssortment']
        async with aiosqlite.connect('databases/assortment.db') as db:
            async with db.execute("SELECT description, price, priceDiscount FROM assortment WHERE name = ?", (productName,)) as cursor:
                result = await cursor.fetchone()

        if result:
            productDescription = result[0]
            productPrice = int(result[1])
            productPriceDiscount = int(result[2])
            productPriceDiscounted = productPrice - productPriceDiscount
            userData[callback.from_user.id]['assortmentCheque'] = userData[callback.from_user.id]['assortmentCount'] * productPriceDiscounted
            

        productPriceDiscountedText = f"{productPrice} ₽" if productPriceDiscount == 0 else f"<s>{productPrice}</s> {productPriceDiscounted} ₽"
        await callback.message.edit_text(f"<b>{productName}</b>\n{productDescription}\n\n"
                            f"Цена за штуку: {productPriceDiscountedText}\n"
                            f"Кол-во: {userData[callback.from_user.id]['assortmentCount']}\n"
                            f"Итоговая цена: {userData[callback.from_user.id]['assortmentCheque']} ₽",
                            reply_markup=kb.assortmentPageButtons)
            

@callbacks.callback_query(F.data == "cartBuy")
async def cbCartBuy(callback: CallbackQuery):
    await callback.message.edit_text(f"🛒 <b>Корзина</b>\n{userData[callback.from_user.id]['assortmentCart']}\n"
                        f"<u>Итоговая сумма: {userData[callback.from_user.id]['assortmentChequeGlobal']} ₽</u>\n\n"
                        f"✅ <b>Заказ отправлен.</b> В скором времени с вами свяжется представитель магазина.")

    linkToUser = f"<a href='https://t.me/{callback.from_user.username}'>{callback.from_user.first_name}</a>" if callback.from_user.username else f"<a href='tg://user?id={callback.from_user.id}'>{callback.from_user.first_name}</a>"
    await callback.bot.send_message(
        chat_id=-1002824873764,
        text=f"🔔 <b>Новый заказ</b>\n"
             f"<u>Заказчик:</u> {linkToUser}\n\n"
             f"🛒 <b>Товары</b>\n{userData[callback.from_user.id]['assortmentCart']}"
             f"<u>Общая сумма:</u> {userData[callback.from_user.id]['assortmentChequeGlobal']} ₽")
    
    userData[callback.from_user.id]['assortmentCart'] = "None"
    userData[callback.from_user.id]['assortmentChequeGlobal'] = 0

@callbacks.callback_query(F.data == "cartClear")
async def cbCartClear(callback: CallbackQuery):
    userData[callback.from_user.id]['assortmentCart'] = "None"
    userData[callback.from_user.id]['assortmentChequeGlobal'] = 0
    await callback.message.edit_text("🛒 <b>Корзина</b>\n<i>Теперь тут пусто...</i>")


# Админский раздел
# /assortment
class assortmentProductAdd(StatesGroup):
    fsmName = State()
    fsmDescription = State()
    fsmPrice = State()
    fsmPriceDiscount = State()

@callbacks.callback_query(F.data == "assortmentAdd")
async def admcmdDatabase(callback: CallbackQuery, state: FSMContext):
    await state.set_state(assortmentProductAdd.fsmName) 
    await callback.message.edit_text("Напишите в следующем сообщении название товара:")

@callbacks.message(assortmentProductAdd.fsmName)
async def admfsmName(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(assortmentProductAdd.fsmDescription)
    await message.answer("Теперь описание товара (допустима любая длинна текста):")

@callbacks.message(assortmentProductAdd.fsmDescription)
async def admfsmDescription(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(assortmentProductAdd.fsmPrice)
    await message.answer("Теперь цена продукта за одну штуку (без скидки):")

@callbacks.message(assortmentProductAdd.fsmPrice)
async def admfsmPrice(message: Message, state: FSMContext):
        try:
            price = int(message.text)
            if price < 0:
                await message.answer("Цена не может быть отрицательной. Введите снова:")
                return
            await state.update_data(price=price)
            await state.set_state(assortmentProductAdd.fsmPriceDiscount)
            await message.answer("Теперь введите скидку (не процент, целое число. 0 для отсутствия. Её можно будет сделать позже):")
        except ValueError:
            await message.answer("Цена должна быть числом. Введите снова:")

@callbacks.message(assortmentProductAdd.fsmPriceDiscount)
async def admfsmPriceDiscount(message: Message, state: FSMContext):
    try:
        priceDiscount = int(message.text)
        data = await state.get_data()
        if priceDiscount < 0:
            await message.answer("Скидка не может быть отрицательной. Введите снова:")
            return
        if priceDiscount > data['price']:
            await message.answer("Скидка не может быть больше цены. Введите снова:")
            return
        await state.update_data(priceDiscount=priceDiscount)
        await state.clear()
        await dba.add(data['name'], data['description'], data['price'], priceDiscount)

        if priceDiscount == 0:
            priceDiscountText = f"{data['price']} ₽"
        else:
            priceDiscounted = data['price'] - priceDiscount
            priceDiscountText = f"<s>{data['price']} ₽</s> {priceDiscounted} ₽ 🔥"

        await message.answer(f"<b>{data['name']}</b>\n{data['description']}\n\nЦена за шт.: {priceDiscountText}")
    except ValueError:
        await message.answer("Скидка должна быть целым числом. Введите снова:")


@callbacks.callback_query(F.data == "assortmentList")
async def cbAssortmentList(callback: CallbackQuery):
    await callback.message.edit_text("Список продуктов в ассортименте и управление ими.",
                                     reply_markup=await kb.assortmentList())

@callbacks.callback_query(F.data.startswith("product_"))
async def cbAssortmentListProductPage(callback: CallbackQuery):
    productNumber = int(callback.data.replace("product_", ""))
    
    async with aiosqlite.connect('databases/assortment.db') as db:
        async with db.execute("SELECT name, description, price, priceDiscount FROM assortment WHERE number = ?", (productNumber,)) as cursor:
            product = await cursor.fetchone()

    if product:
        name, description, price, discount = product
        if discount == 0:
            priceDiscountText = f"{price} ₽"
        else:
            priceDiscounted = price - discount
            priceDiscountText = f"<s>{price}</s> {priceDiscounted} ₽ 🔥"
        
        await callback.message.edit_text(
            f"<b>#{productNumber} - {name}</b>\n{description}\n\nЦена: {priceDiscountText}",
            reply_markup=kb.assortmentListActions_(productNumber)
        )
    else:
        await callback.answer("Товар не найден")

@callbacks.callback_query(F.data.startswith("assortmentListActionsDelete_"))
async def cbAssortmentListActionsDelete(callback: CallbackQuery):
    productNumber = int(callback.data.replace("assortmentListActionsDelete_", ""))
    await dba.delete(productNumber)

    await callback.answer(f"Товар №{productNumber} удалён.")
    await callback.message.edit_text("Список продуктов в ассортименте и управление ими.",
                                     reply_markup=await kb.assortmentList())


# /posts
class postsAdd(StatesGroup):
    fsmText = State()
    fsmTime = State()

@callbacks.callback_query(F.data == "postsAdd")
async def cbPostsAdd(callback: CallbackQuery, state: FSMContext):
    await state.set_state(postsAdd.fsmText)
    await callback.message.edit_text("Напишите содержание поста:",
                                     reply_markup=None)

@callbacks.message(postsAdd.fsmText)
async def admfsmPostText(message: Message, state: FSMContext):
    await state.update_data(text=message.html_text)
    await state.set_state(postsAdd.fsmTime)
    await message.answer("Укажите время отправки (формат: ДД.ММ ЧЧ:ММ):")

@callbacks.message(postsAdd.fsmTime)
async def process_post_time(message: Message, state: FSMContext):
    try:
        timeStr = message.text.strip()
        timeIntNow = datetime.now()
        
        # Парсим время
        post_time = datetime.strptime(timeStr, "%d.%m %H:%M").replace(year=timeIntNow.year)   
        
        # Проверяем, что время не в прошлом
        if post_time <= timeIntNow:
            await message.answer("❌ Время должно быть в будущем! Попробуйте снова.")
            return
            
        # Получаем сохраненный текст из состояния
        data = await state.get_data()
        post_text = data.get('text')
        
        # Добавляем в базу данных
        await dbp.add(post_text, post_time, CHANNEL)
        
        await message.answer(f"✅ Пост успешно запланирован на {post_time.strftime('%d.%m %H:%M')}")
        
        # Очищаем состояние
        await state.clear()

    except ValueError:
        await message.answer("❌ Неверный формат времени! Используйте: ДД.ММ ЧЧ:ММ\nПопробуйте снова.")
    except Exception as e:
        await message.answer("Произошла непредвиденная ошибка.")
        print(f"Ошибка при планировании поста: {e}")
        await state.clear()


'''
@callbacks.callback_query(F.data == "postsList")
async def cbPostsList(callback: CallbackQuery):
    await callback.message.edit_text("Список запланированных постов:", reply_markup=await kb.postsListKeyboard())
'''