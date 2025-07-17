# ===================================================
# File 1: bot.py
# ===================================================
# -*- coding: utf-8 -*-
import logging
import datetime
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# --- Configuration ---
# This reads the BOT_TOKEN from Render's environment variables.
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# --- Your Links ---
# All links are now updated as per your request.
TELEGRAM_GROUP_URL = "https://t.me/kaviancoin"
TELEGRAM_CHANNEL_URL = "https://t.me/kavianai"
YOUTUBE_URL = "https://youtube.com/@boombitz"
INSTAGRAM_URL = "https://www.instagram.com/hzvideolab/"
TWITTER_URL = "https://x.com/KavianCoin"
AI_WEBSITE_URL = "https://Kavian.ai"
MAIN_WEBSITE_URL = "https://kavcoin.xyz"
TOKEN_PAGE_URL = "https://jup.ag/tokens/AX6fPqzs5vupRQ6B8LryLAMrDw7D18dDXQAJKMSUTLSF"

# --- Bot Data Storage (In-memory) ---
# Note: This data will be lost if the bot restarts.
user_progress = {}
user_language = {}

# --- Setup Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Text and Translations ---
# All user-facing text is stored here for easy editing.
LANGUAGES = {
    'fa': {
        "tasks": [
            {"intro": "1️⃣ لطفا به گروه تلگرام ما بپیوندید.", "button_text": "عضویت در گروه 💬", "url": TELEGRAM_GROUP_URL},
            {"intro": "2️⃣ عالی! حالا در کانال تلگرام ما مشترک شوید.", "button_text": "اشتراک در کانال 📢", "url": TELEGRAM_CHANNEL_URL},
            {"intro": "3️⃣ لطفا کانال یوتیوب ما را دنبال کنید.", "button_text": "اشتراک در یوتیوب 🎬", "url": YOUTUBE_URL},
            {"intro": "4️⃣ صفحه اینستاگرام ما را دنبال کنید.", "button_text": "دنبال کردن در اینستاگرام 📱", "url": INSTAGRAM_URL},
            {"intro": "5️⃣ صفحه ایکس (توییتر) ما را دنبال کنید.", "button_text": "دنبال کردن در ایکس 🐦", "url": TWITTER_URL},
            {"intro": "6️⃣ از وب‌سایت هوش مصنوعی ما استفاده کنید.", "button_text": "استفاده از وب‌سایت AI 🤖", "url": AI_WEBSITE_URL},
            {"intro": "7️⃣ از وب‌سایت اصلی ما دیدن کنید.", "button_text": "بازدید از وب‌سایت 🌐", "url": MAIN_WEBSITE_URL},
            {"intro": "8️⃣ برای خرید توکن، از صفحه توکن ما دیدن کنید.", "button_text": "خرید توکن ما ❤️", "url": TOKEN_PAGE_URL},
        ],
        "final_message": "🎉 تبریک! شما تمام وظایف را با موفقیت انجام دادید. مدارک شما به زودی بررسی خواهد شد.",
        "screenshot_request": "👍 عالی! حالا لطفا یک اسکرین‌شات به عنوان مدرک برای وظیفه {task_num} ارسال کنید.",
        "done_button": "✅ انجام دادم، آماده ارسال مدرک",
        "proof_received": "✅ متشکریم! مدرک شما دریافت شد. این هم وظیفه بعدی:",
        "select_language_prompt": "لطفاً زبان خود را انتخاب کنید. / Please select your language."
    },
    'en': {
        "tasks": [
            {"intro": "1️⃣ Please join our Telegram Group.", "button_text": "Join Group 💬", "url": TELEGRAM_GROUP_URL},
            {"intro": "2️⃣ Great! Now, subscribe to our Telegram Channel.", "button_text": "Subscribe to Channel 📢", "url": TELEGRAM_CHANNEL_URL},
            {"intro": "3️⃣ Please subscribe to our YouTube Channel.", "button_text": "Subscribe on YouTube 🎬", "url": YOUTUBE_URL},
            {"intro": "4️⃣ Follow our Instagram Page.", "button_text": "Follow on Instagram 📱", "url": INSTAGRAM_URL},
            {"intro": "5️⃣ Follow our X (Twitter) Page.", "button_text": "Follow on X 🐦", "url": TWITTER_URL},
            {"intro": "6️⃣ Use our AI Website.", "button_text": "Use AI Website 🤖", "url": AI_WEBSITE_URL},
            {"intro": "7️⃣ Visit our main Website.", "button_text": "Visit Website 🌐", "url": MAIN_WEBSITE_URL},
            {"intro": "8️⃣ To buy our token, visit our Token Page.", "button_text": "Visit our Token Page ❤️", "url": TOKEN_PAGE_URL},
        ],
        "final_message": "🎉 Congratulations! You have successfully completed all tasks. Your submissions will be reviewed shortly.",
        "screenshot_request": "👍 Great! Now, please send a screenshot as proof for Task {task_num}.",
        "done_button": "✅ Done, Ready to Send Proof",
        "proof_received": "✅ Thank you! Your proof has been received. Here is the next task:",
        "select_language_prompt": "Please select your language. / لطفاً زبان خود را انتخاب کنید."
    }
}

# --- Bot Logic ---

async def advance_flow(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Sends the next task or completion message based on user progress."""
    lang = user_language.get(chat_id, 'fa') # Default to Persian
    texts = LANGUAGES[lang]
    tasks = texts["tasks"]
    
    step = user_progress.get(chat_id, 0)
    task_index = step // 2
    is_screenshot_step = step % 2 != 0

    if task_index >= len(tasks):
        # User has finished all tasks
        await context.bot.send_message(chat_id=chat_id, text=texts["final_message"])
        return

    if is_screenshot_step:
        # Ask for a screenshot
        screenshot_request_text = texts["screenshot_request"].format(task_num=task_index + 1)
        await context.bot.send_message(chat_id=chat_id, text=screenshot_request_text)
    else:
        # Send the next task
        task = tasks[task_index]
        buttons = [
            [InlineKeyboardButton(task["button_text"], url=task["url"])],
            [InlineKeyboardButton(texts["done_button"], callback_data="task_done")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await context.bot.send_message(chat_id=chat_id, text=task["intro"], reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command and shows language selection."""
    user = update.effective_user
    logger.info(f"User {user.first_name} ({user.id}) started the bot.")
    
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data="select_lang_en")],
        [InlineKeyboardButton("🇮🇷 فارسی (Persian)", callback_data="select_lang_fa")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(LANGUAGES['en']['select_language_prompt'], reply_markup=reply_markup)

async def language_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles language selection and starts the task flow."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang_code = query.data.split('_')[-1]
    user_language[user_id] = lang_code
    
    user_progress[user_id] = 0 # Start from the first task
    await query.message.delete()
    await advance_flow(context, user_id)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the 'Done' button press."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id not in user_language:
        await query.message.reply_text("Please /start the bot again to select a language.")
        return

    if query.data == "task_done":
        await query.message.delete()
        if user_id in user_progress:
            user_progress[user_id] += 1
            await advance_flow(context, user_id)

async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles photo submissions as proof."""
    user_id = update.effective_user.id
    if user_id not in user_language:
        await update.message.reply_text("Please /start the bot again to select a language.")
        return

    lang = user_language[user_id]
    texts = LANGUAGES[lang]
    step = user_progress.get(user_id, -1)
    is_screenshot_step = step % 2 != 0

    if is_screenshot_step:
        await update.message.reply_text(texts["proof_received"])
        user_progress[user_id] += 1
        await advance_flow(context, user_id)
    else:
        logger.info(f"User {user_id} sent a photo when it was not expected.")

def main() -> None:
    """Starts the bot."""
    if not BOT_TOKEN:
        logger.error("FATAL: BOT_TOKEN environment variable is not set.")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(language_selection_handler, pattern="^select_lang_"))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^task_done$"))
    application.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))
    
    logger.info("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
