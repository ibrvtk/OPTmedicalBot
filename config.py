from aiogram import Bot
from aiogram.client.default import DefaultBotProperties



TOKEN = '' #*
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))


CHANNEL = '' #*
ADMINCHATS = [-100] #*
ADMINUSERS = [] #*

userData = {}


shopName = "🔵 <b>OPT MEDICAL</b>"
shopDescription = "\nОптовые поставки контурной пластики!\nВыгодные условия для косметологов и клиник.\n\nПрямые поставки от производителях — качество и доступность 🤝\n\nЗаказы принимаем 24/7\nДоставка по РФ 🇷🇺"

kayboardPlaceholderChoose = "Выберите..."
errorCountNull = "Меньше одного товара!"