from config import CHANNEL, ADMINCHATS, ADMINUSERS, userData
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



# 📄 Ассортимент
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
    allAdmins = ADMINCHATS + ADMINUSERS
    for recipients in allAdmins:
        try:
            await callback.bot.send_message(
                chat_id=recipients,
                text=f"🔔 <b>Новый заказ</b>\n"
                    f"<u>Заказчик:</u> {linkToUser}\n\n"
                    f"🛒 <b>Товары</b>\n{userData[callback.from_user.id]['assortmentCart']}"
                    f"<u>Общая сумма:</u> {userData[callback.from_user.id]['assortmentChequeGlobal']} ₽")
        except Exception as e:
            print(f"Ошибка отправки {recipients}: {e}")
    
    userData[callback.from_user.id]['assortmentCart'] = "None"
    userData[callback.from_user.id]['assortmentChequeGlobal'] = 0

@callbacks.callback_query(F.data == "cartClear")
async def cbCartClear(callback: CallbackQuery):
    userData[callback.from_user.id]['assortmentCart'] = "None"
    userData[callback.from_user.id]['assortmentChequeGlobal'] = 0
    await callback.message.edit_text("🛒 <b>Корзина</b>\n<i>Теперь тут пусто...</i>")


# Админский раздел
# /assortment
@callbacks.callback_query(F.data == "assortmentList")
async def cbAssortmentList(callback: CallbackQuery):
    await callback.message.edit_text("Список продуктов в ассортименте и управление ими.",
                                     reply_markup=await kb.assortmentList())
    
@callbacks.callback_query(F.data == "assortmentListBack")
async def cbPostsListActionsBack(callback: CallbackQuery):
    await callback.message.edit_text("Управление ассортиментом.",
                                     reply_markup=kb.assortmentKeyboard)


# callback "assortmentAdd"
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
            await message.answer("Теперь введите скидку (не %, но целое число) (0 для её отсутствия) (можно будет сделать позже):")

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


# callback "assortmentList"
@callbacks.callback_query(F.data.startswith("product_"))
async def cbAssortmentListProductPage(callback: CallbackQuery):
    productNumber = int(callback.data.replace("product_", ""))
    
    async with aiosqlite.connect('databases/assortment.db') as db:
        async with db.execute("SELECT name, description, price, priceDiscount FROM assortment WHERE number = ?", (productNumber,)) as cursor:
            product = await cursor.fetchone()

        name, description, price, discount = product
        if discount == 0:
            priceDiscountText = f"{price} ₽"
        else:
            priceDiscounted = price - discount
            priceDiscountText = f"<s>{price}</s> {priceDiscounted} ₽ 🔥"
        
        await callback.message.edit_text(f"<b>№{productNumber} - {name}</b>\n{description}\n\nЦена: {priceDiscountText}",
                                         reply_markup=kb.assortmentListActions_(productNumber))


class admfsmPriceDiscount(StatesGroup):
    newPriceDiscount = State()

@callbacks.callback_query(F.data.startswith("assortmentListActionsNewPriceDiscount_"))
async def cbAssortmentListActionsNewPriceDiscount(callback: CallbackQuery, state: FSMContext):
    productNumber = int(callback.data.replace("assortmentListActionsNewPriceDiscount_", ""))
    await state.update_data(productNumber=productNumber)
    await state.set_state(admfsmPriceDiscount.newPriceDiscount)

    await callback.message.edit_text("Введите скидку на товар (не в виде %) (0 для отмены или удаления существующей) "
                                     "(если скидка уже есть и её нужно поменять, просто введите новое значене, они не суммируются):")

@callbacks.message(admfsmPriceDiscount.newPriceDiscount)
async def admfsmAssortmentListActionsNewPriceDiscount(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        productNumber = data['productNumber']

        async with aiosqlite.connect('databases/assortment.db') as db:
            async with db.execute("SELECT price FROM assortment WHERE number = ?", (productNumber,)) as cursor:
                result = await cursor.fetchone()

        productPrice = result[0]
        priceDiscount = int(message.text)

        if priceDiscount < 0:
            await message.answer("Скидка не может быть отрицательной. Введите снова:")
            return
        if priceDiscount > productPrice:
            await message.answer("Скидка не может быть больше цены. Введите снова:")
            return

        async with aiosqlite.connect('databases/assortment.db') as db:
            await db.execute("UPDATE assortment SET priceDiscount = ? WHERE number = ?",  (priceDiscount, productNumber))
            await db.commit()

        await state.clear()
        
        if priceDiscount == 0:
            await message.answer(f"Скидка товару №{productNumber} убрана.")
        else:
            await message.answer(f"Товару №{productNumber} установлена скидка {priceDiscount} ₽")
        
    except ValueError:
        await message.answer("Скидка должна быть целым числом. Введите снова:")


class admfsmNewDescription(StatesGroup):
    newDescription = State()

@callbacks.callback_query(F.data.startswith("assortmentListActionsNewDescription_"))
async def cbPostsListActionsNewText(callback: CallbackQuery, state: FSMContext):
    productNumber = int(callback.data.replace("assortmentListActionsNewDescription_", ""))
    await state.update_data(productNumber=productNumber)
    await state.set_state(admfsmNewDescription.newDescription)

    await callback.message.edit_text("Введите новое описание товара:")

@callbacks.message(admfsmNewDescription.newDescription)
async def admfsmAssortmentListActionsNewText(message: Message, state: FSMContext):
        data = await state.get_data()
        productNumber = data['productNumber']
        priceDescription = message.text

        async with aiosqlite.connect('databases/assortment.db') as db:
            await db.execute("UPDATE assortment SET description = ? WHERE number = ?",  (priceDescription, productNumber))
            await db.commit()

        await state.clear()
        
        await message.answer(f"Товару №{productNumber} изменено описание:\n{priceDescription}")    


@callbacks.callback_query(F.data.startswith("assortmentListActionsDelete_"))
async def cbPostsListActionsDelete(callback: CallbackQuery):
    productNumber = int(callback.data.replace("assortmentListActionsDelete_", ""))
    await dba.delete(productNumber)

    await callback.answer(f"Товар №{productNumber} удалён.")
    await callback.message.edit_text("Список продуктов в ассортименте и управление ими.",
                                     reply_markup=await kb.assortmentList())
    

@callbacks.callback_query(F.data == "assortmentListActionsBack")
async def cbPostsListActionsBack(callback: CallbackQuery):
    await callback.message.edit_text("Список продуктов в ассортименте и управление ими.",
                                     reply_markup=await kb.assortmentList())


# /posts
@callbacks.callback_query(F.data == "postsList")
async def cbAssortmentList(callback: CallbackQuery):
    await callback.message.edit_text("Список запланированных постов и управление ими.",
                                     reply_markup=await kb.postsList())
    
@callbacks.callback_query(F.data == "postsListBack")
async def cbPostsListActionsBack(callback: CallbackQuery):
    await callback.message.edit_text("Управление отложенными постами.",
                                     reply_markup=kb.postsKeyboard)


# callback "postsAdd"
class postsAdd(StatesGroup):
    fsmText = State()
    fsmTime = State()

@callbacks.callback_query(F.data == "postsAdd")
async def cbPostsAdd(callback: CallbackQuery, state: FSMContext):
    await state.set_state(postsAdd.fsmText)
    await callback.message.edit_text("Напишите содержание поста:",
                                     reply_markup=None)

@callbacks.message(postsAdd.fsmText)
async def admfsmPostsText(message: Message, state: FSMContext):
    await state.update_data(text=message.html_text)
    await state.set_state(postsAdd.fsmTime)
    await message.answer("Укажите время отправки (ДД.ММ ЧЧ:ММ):")

@callbacks.message(postsAdd.fsmTime)
async def admfsmPostsTime(message: Message, state: FSMContext):
    try:
        timeStr = message.text.strip()
        timeIntNow = datetime.now()
        postTime = datetime.strptime(timeStr, "%d.%m %H:%M").replace(year=timeIntNow.year)   
        
        if postTime <= timeIntNow:
            await message.answer("Время должно быть в будущем. Введите снова:")
            return
            
        data = await state.get_data()
        postText = data.get('text')
        await dbp.add(postText, postTime, CHANNEL)
        await state.clear()
        
        await message.answer(f"Пост запланирован на {postTime.strftime('%d.%m %H:%M')}.")

    except ValueError:
        await message.answer("Неверный формат времени (нужно ДД.ММ ЧЧ:ММ). Введите снова:")

    except Exception as e:
        await message.answer("Произошла непредвиденная ошибка.")
        print(f"Ошибка при планировании поста: {e}")
        await state.clear()


# callback "postsList"
@callbacks.callback_query(F.data.startswith("post_"))
async def cbPostsListPostPage(callback: CallbackQuery):
    postId = int(callback.data.replace("post_", ""))
    
    async with aiosqlite.connect('databases/posts.db') as db:
        async with db.execute("SELECT text, time, channel_id FROM posts WHERE post_id = ?", (postId,)) as cursor:
            post = await cursor.fetchone()

        text, time, channel_id = post

        await callback.message.edit_text(f"<blockquote>{text}</blockquote>\n\nПланируется выложить {time}\nВ канал {channel_id}",
                                         reply_markup=kb.postsListActions_(postId))


class admfsmPostsNewTime(StatesGroup):
    newTime = State()

@callbacks.callback_query(F.data.startswith("postsListActionsNewTime_"))
async def cbPostsListActionsNewTime(callback: CallbackQuery, state: FSMContext):
    postId = int(callback.data.replace("postsListActionsNewTime_", ""))
    await state.update_data(postId=postId)
    await state.set_state(admfsmPostsNewTime.newTime)

    await callback.message.edit_text("Введите новое время публикации (ДД.ММ ЧЧ:ММ):")

@callbacks.message(admfsmPostsNewTime.newTime)
async def admfsmPostsListActionsNewTime(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        postId = data['postId']

        timeStr = message.text.strip()
        timeIntNow = datetime.now()
        postTime = datetime.strptime(timeStr, "%d.%m %H:%M").replace(year=timeIntNow.year)   

        if postTime <= timeIntNow:
            await message.answer("Время должно быть в будущем. Введите снова:")
            return
            
        async with aiosqlite.connect('databases/posts.db') as db:
            await db.execute("UPDATE posts SET time = ? WHERE post_id = ?", (postTime, postId))
            await db.commit()
        
        await state.clear()

        await message.answer(f"Время публикации поста изменено на {postTime.strftime('%d.%m %H:%M')}")

    except ValueError:
        await message.answer("Неверный формат времени (нужно ДД.ММ ЧЧ:ММ). Введите снова:")

    except Exception as e:
        await message.answer("Произошла непредвиденная ошибка.")
        print(f"Ошибка при изменении времени поста: {e}")
        await state.clear()


class admfsmPostsNewText(StatesGroup):
    newText = State()

@callbacks.callback_query(F.data.startswith("postsListActionsNewText_"))
async def cbPostsListActionsNewText(callback: CallbackQuery, state: FSMContext):
    postId = int(callback.data.replace("postsListActionsNewText_", ""))
    await state.update_data(postId=postId)
    await state.set_state(admfsmPostsNewText.newText)

    await callback.message.edit_text("Введите новый текст:")

@callbacks.message(admfsmPostsNewText.newText)
async def admfsmPostsListActionsNewText(message: Message, state: FSMContext):
        data = await state.get_data()
        postId = data['postId']
        postNewText = message.text

        async with aiosqlite.connect('databases/posts.db') as db:
            await db.execute("UPDATE posts SET text = ? WHERE post_id = ?",  (postNewText, postId))
            await db.commit()

        await state.clear()
        
        await message.answer(f"Посту №{postId} изменено содержание:\n<blockquote>{postNewText}</blockquote>")    


@callbacks.callback_query(F.data.startswith("postsActionsDelete_"))
async def cbPostsListActionsDelete(callback: CallbackQuery):
    postId = int(callback.data.replace("postsActionsDelete_", ""))
    await dbp.delete(postId)

    await callback.answer(f"Пост №{postId} удалён.")
    await callback.message.edit_text("Список запланированных постов и управление ими.",
                                     reply_markup=await kb.postsList())
    

@callbacks.callback_query(F.data == "postsListActionsBack")
async def cbPostsListActionsBack(callback: CallbackQuery):
    await callback.message.edit_text("Список запланированных постов и управление ими.",
                                     reply_markup=await kb.postsList())