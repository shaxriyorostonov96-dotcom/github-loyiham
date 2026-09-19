import os
import time
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import telebot
from telebot import types
from groq import Groq


# ==================================================
# CHATUZB AI
# ==================================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

CHANNEL_USERNAME = "@shaxriyordasturchi_uz"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ==================================================
# ENVIRONMENT TEKSHIRISH
# ==================================================

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN topilmadi!")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY topilmadi!")


# ==================================================
# BOT
# ==================================================

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)


# ==================================================
# SHAXRIYOR HAQIDA
# ==================================================

SHAXRIYOR_INFO = """
Dasturchi Ostonov Shaxriyor — ChatUZB AI loyihasini yaratgan dasturchi.

Shaxriyor IT va dasturlashga qiziqadi hamda HTML, CSS, JavaScript,
Python va Telegram botlar bilan ishlaydi.

U Junior IT Academy'da IT va dasturlashni o‘rganmoqda.

Shaxriyor ChatUZB AI loyihasini foydalanuvchilarga savollarga javob
beradigan aqlli Telegram yordamchi sifatida ishlab chiqmoqda.

Telegram kanali: @shaxriyordasturchi_uz
"""


# ==================================================
# KANAL OBUNASINI TEKSHIRISH
# ==================================================

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(
            CHANNEL_USERNAME,
            user_id
        )

        return member.status in [
            "creator",
            "administrator",
            "member"
        ]

    except Exception as e:
        logging.error(f"Kanal tekshirish xatosi: {e}")
        return False


def subscription_message(chat_id):

    markup = types.InlineKeyboardMarkup()

    button = types.InlineKeyboardButton(
        "📢 Kanalga obuna bo‘lish",
        url="https://t.me/shaxriyordasturchi_uz"
    )

    check_button = types.InlineKeyboardButton(
        "✅ Obunani tekshirish",
        callback_data="check_subscription"
    )

    markup.add(button)
    markup.add(check_button)

    bot.send_message(
        chat_id,
        "🔒 <b>ChatUZB AI'dan foydalanish uchun "
        "kanalga obuna bo‘ling.</b>\n\n"
        "1️⃣ Kanalga kiring\n"
        "2️⃣ <b>Obuna bo‘lish</b> tugmasini bosing\n"
        "3️⃣ Keyin <b>Obunani tekshirish</b> tugmasini bosing.",
        parse_mode="HTML",
        reply_markup=markup
    )


# ==================================================
# START
# ==================================================

@bot.message_handler(commands=["start"])
def start(message):

    if not check_subscription(message.from_user.id):
        subscription_message(message.chat.id)
        return

    first_name = message.from_user.first_name or "Do‘st"

    bot.send_message(
        message.chat.id,
        f"👋 Assalomu alaykum, <b>{first_name}</b>!\n\n"
        "🤖 Men <b>ChatUZB AI</b>man.\n\n"
        "👨‍💻 Men <b>Dasturchi Ostonov Shaxriyor</b> "
        "tomonidan yaratildim.\n\n"
        "💬 Savolingizni yozing, men javob beraman.",
        parse_mode="HTML"
    )


# ==================================================
# OBUNANI TEKSHIRISH
# ==================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "check_subscription"
)
def check_subscription_callback(call):

    if check_subscription(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "✅ Obuna tasdiqlandi!"
        )

        bot.send_message(
            call.message.chat.id,
            "✅ <b>Obuna tasdiqlandi!</b>\n\n"
            "🤖 Endi ChatUZB AI'dan foydalanishingiz mumkin.",
            parse_mode="HTML"
        )

    else:

        bot.answer_callback_query(
            call.id,
            "❌ Siz hali kanalga obuna bo‘lmagansiz.",
            show_alert=True
        )


# ==================================================
# GROQ AI
# ==================================================

def ask_ai(user_text):

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Sen ChatUZB AI nomli aqlli yordamchisan. "
                    "Foydalanuvchiga aniq, tushunarli va foydali "
                    "javob ber. "
                    "Agar foydalanuvchi boshqa tilda yozsa, "
                    "shu tilda javob ber."
                )
            },
            {
                "role": "user",
                "content": user_text
            }
        ],
        temperature=0.7,
        max_tokens=2048
    )

    return response.choices[0].message.content


# ==================================================
# MATN XABARLARI
# ==================================================

@bot.message_handler(content_types=["text"])
def handle_message(message):

    if not check_subscription(message.from_user.id):
        subscription_message(message.chat.id)
        return

    user_text = message.text.strip()
    text_lower = user_text.lower()

    # SHAXRIYOR HAQIDA

    shaxriyor_words = [
        "shaxriyor kim",
        "shaxriyor haqida",
        "dasturchi ostonov shaxriyor",
        "ostonov shaxriyor kim",
        "dasturchi ostonov shaxriyor haqida",
        "shaxriyor haqida malumot",
        "shaxriyor haqida ma'lumot"
    ]

    if any(word in text_lower for word in shaxriyor_words):

        bot.send_message(
            message.chat.id,
            SHAXRIYOR_INFO
        )

        return

    # KIM YARATDI

    creator_words = [
        "seni kim yaratdi",
        "seni kim yasadi",
        "kim yaratgan",
        "kim yasagan",
        "yaratuvching kim",
        "seni kim tuzgan",
        "kim tuzgan",
        "seni kim ishlab chiqdi"
    ]

    if text_lower in creator_words:

        bot.send_message(
            message.chat.id,
            "🤖 Men <b>Dasturchi Ostonov Shaxriyor</b> "
            "tomonidan yaratildim.",
            parse_mode="HTML"
        )

        return

    # ISM

    if text_lower in [
        "isming nima",
        "isming",
        "sen kimsan"
    ]:

        bot.send_message(
            message.chat.id,
            "🤖 Mening ismim <b>ChatUZB AI</b>.",
            parse_mode="HTML"
        )

        return

    # SALOM

    if text_lower in [
        "salom",
        "assalomu alaykum",
        "hello",
        "hi"
    ]:

        bot.send_message(
            message.chat.id,
            "👋 Assalomu alaykum!\n\n"
            "Men <b>ChatUZB AI</b>man. "
            "Savolingizni yozing, yordam beraman.",
            parse_mode="HTML"
        )

        return

    # AI

    try:

        bot.send_chat_action(
            message.chat.id,
            "typing"
        )

        answer = ask_ai(user_text)

        bot.send_message(
            message.chat.id,
            answer
        )

    except Exception as e:

        logging.error(f"Groq xatosi: {e}")

        bot.send_message(
            message.chat.id,
            "⚠️ Hozircha AI serverida muammo yuz berdi.\n\n"
            "Iltimos, birozdan keyin qayta urinib ko‘ring."
        )


# ==================================================
# RASM
# ==================================================

@bot.message_handler(content_types=["photo"])
def handle_photo(message):

    if not check_subscription(message.from_user.id):
        subscription_message(message.chat.id)
        return

    bot.reply_to(
        message,
        "🖼️ Rasm qabul qilindi!"
    )


# ==================================================
# VIDEO
# ==================================================

@bot.message_handler(content_types=["video"])
def handle_video(message):

    if not check_subscription(message.from_user.id):
        subscription_message(message.chat.id)
        return

    bot.reply_to(
        message,
        "🎥 Video qabul qilindi!"
    )


# ==================================================
# FAYL
# ==================================================

@bot.message_handler(content_types=["document"])
def handle_document(message):

    if not check_subscription(message.from_user.id):
        subscription_message(message.chat.id)
        return

    bot.reply_to(
        message,
        "📁 Fayl qabul qilindi!"
    )


# ==================================================
# LOKATSIYA
# ==================================================

@bot.message_handler(content_types=["location"])
def handle_location(message):

    if not check_subscription(message.from_user.id):
        subscription_message(message.chat.id)
        return

    latitude = message.location.latitude
    longitude = message.location.longitude

    bot.reply_to(
        message,
        f"📍 Lokatsiya qabul qilindi!\n\n"
        f"Latitude: {latitude}\n"
        f"Longitude: {longitude}"
    )


# ==================================================
# RENDER PORT SERVER
# ==================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)
        self.send_header(
            "Content-type",
            "text/plain"
        )
        self.end_headers()

        self.wfile.write(
            b"ChatUZB AI is running!"
        )

    def log_message(self, format, *args):
        return


def start_server():

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    print(
        f"🌐 HTTP server {port}-portda ishlayapti..."
    )

    server.serve_forever()


# ==================================================
# ISHGA TUSHIRISH
# ==================================================

if __name__ == "__main__":

    print()
    print("=" * 50)
    print("CHATUZB AI BOT")
    print("Professional AI Assistant")
    print("=" * 50)

    # Render uchun HTTP server
    server_thread = threading.Thread(
        target=start_server,
        daemon=True
    )

    server_thread.start()

    # Telegram bot
    while True:

        try:

            print(
                "🤖 Telegram bot ishlayapti!"
            )

            bot.infinity_polling(
                timeout=60,
                long_polling_timeout=60,
                skip_pending=True
            )

        except Exception as e:

            logging.error(
                f"Bot xatosi: {e}"
            )

            print(
                "🔄 5 soniyadan keyin "
                "qayta ishga tushadi..."
            )

            time.sleep(5)
