from aiogram import Bot
from aiogram.client.default import DefaultBotProperties



TOKEN = '' # Токен бота.
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))


CHANNEL = -100 # Telegram ID канала, куда будут присылаться посты из команды /posts.
ADMINCHATS = [-100] # Список бесед админов. В них будут присылаться уведомления о заказах и через них можно настраивать бота.
ADMINUSERS = [] # Список админов. Им будут присылаться уведомления о заказах и они могут настраивать бота в ЛС с ним.

userData = {}


shopName = "🔵 <b>OPT MEDICAL</b>"
shopDescription = "\nОптовые поставки контурной пластики!\nВыгодные условия для косметологов и клиник.\n\nПрямые поставки от производителях — качество и доступность 🤝\n\nЗаказы принимаем 24/7\nДоставка по РФ 🇷🇺"

kayboardPlaceholderChoose = "Выберите..."
errorCountNull = "Меньше одного товара!"