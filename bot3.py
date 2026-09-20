import os
import telebot
from flask import Flask
from threading import Thread
from telebot.types import ChatJoinRequest

# ===== КОНФИГ =====
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("❌ Нет токена! Добавь TELEGRAM_TOKEN в переменные Render.")

ADMIN_CHAT_ID = 8842769815  # ЗАМЕНИ НА СВОЙ ID (число)

bot = telebot.TeleBot(TOKEN)

# ===== КНОПКИ =====
def main_kb():
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("🔓 Получить доступ", callback_data="get"))
    return kb

def pay_kb():
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("✅ Я оплатил(а)", callback_data="paid"))
    return kb

# ===== СТАРТ =====
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет.\n\n"
        "Ты попал(а) в официальный бот доступа к библиотеке Женька.\n\n"
        "Что внутри:\n"
        "• Отборный контент\n"
        "• Лучшее качество\n"
        "• Эксклюзив\n\n"
        "Стоимость доступа — 700 ₽.\n\n"
        "Нажми кнопку ниже, чтобы получить реквизиты.",
        reply_markup=main_kb()
    )

# ===== ОПЛАТА =====
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "get":
        bot.edit_message_text(
            "💳 Реквизиты для оплаты:\n\n"
            "Карта: 5379 6530 1364 0105\n"
            "Сумма: 700 ₽\n"
            "После перевода нажми «Я оплатил(а)» и пришли скриншот.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=pay_kb()
        )
        bot.answer_callback_query(call.id)

    elif call.data == "paid":
        bot.edit_message_text(
            "📸 Отправь скриншот перевода.\n\n"
            "После проверки я предоставлю тебе доступ.",
            call.message.chat.id,
            call.message.message_id
        )
        bot.answer_callback_query(call.id)

# ===== СКРИНШОТ =====
@bot.message_handler(content_types=['photo'])
def screenshot(message):
    user = message.from_user
    uid = user.id
    name = user.full_name
    username = user.username or "нет username"

    admin_text = (
        f"🔔 *Новая заявка*\n"
        f"━━━━━━━━━━━━━━\n"
        f"Имя: {name}\n"
        f"ID: `{uid}`\n"
        f"Юзернейм: @{username}\n"
    )

    bot.send_message(ADMIN_CHAT_ID, admin_text, parse_mode="Markdown")
    bot.send_photo(ADMIN_CHAT_ID, message.photo[-1].file_id, caption="🧾 Скриншот оплаты")
    bot.reply_to(message, "✅ Принято. Я проверю оплату и предоставлю доступ.")

# ===== ЗАЯВКИ В КАНАЛ =====
@bot.chat_join_request_handler()
def join_request(request: ChatJoinRequest):
    bot.send_message(
        request.from_user.id,
        "👋 Ты подал(а) заявку в приватную библиотеку Женька.\n\n"
        "💰 Доступ стоит — 700 ₽.\n"
        "Для оплаты нажми /start в этом боте."
 	"После оплаты я добавлю тебя в канал."
    )

# ===== ЗАПУСК =====
def run_bot():
    bot.remove_webhook()
    print("🤖 Бот запущен")
    bot.infinity_polling()

# ===== ВЕБ-СЕРВЕР =====
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

@app.route('/health')
def health():
    return "OK"

if __name__ == "__main__":
    Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)