import asyncio
import os
import aiohttp
import schedule
import time
import threading
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8823422105:AAG-mhQurbbqUp4KyhEdn0qQN_CGQFu4Qt4"
CHAT_ID = "8881529092"
RAPIDAPI_KEY = "4cd80b1366msh9918c7a2780a5bep11e5bbjsn3620f2094de1"

async def send_message(context, chat_id, text):
    await context.bot.send_message(chat_id=chat_id, text=text)

async def send_video(context, chat_id, video_bytes, caption):
    await context.bot.send_video(chat_id=chat_id, video=video_bytes, caption=caption)

async def scrape_and_send(context, chat_id):
    try:
        url = "https://tiktok-video-no-watermark2.p.rapidapi.com/feed/search"
        params = {"keywords": "fineshyt pinay viral", "region": "PH", "count": "5"}
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "tiktok-video-no-watermark2.p.rapidapi.com"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                data = await resp.json()
        videos = data.get("data", {}).get("videos", [])
        if not videos:
            await send_message(context, chat_id, "No new videos found.")
            return
        await send_message(context, chat_id, f"Found {len(videos)} videos. Sending top {min(len(videos), 3)}...")
        for i, video in enumerate(videos[:3]):
            video_url = video.get("play")
            desc = video.get("title", "No description")
            async with session.get(video_url) as video_resp:
                video_bytes = await video_resp.read()
            await send_video(context, chat_id, video_bytes, f"@fineshyt viral pinay\n{desc}")
    except Exception as e:
        await send_message(context, chat_id, f"Scrape failed: {str(e)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    button = KeyboardButton("Scrappe")
    reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
    await update.message.reply_text("Click Scrappe button to manually scrape TikTok videos now.", reply_markup=reply_markup)

async def scrappe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await send_message(context, chat_id, "Manual scrape triggered. Fetching latest videos...")
    await scrape_and_send(context, chat_id)

async def cron_job(context: ContextTypes.DEFAULT_TYPE):
    await scrape_and_send(context, CHAT_ID)

def run_schedule(app):
    schedule.every().day.at("08:00").do(lambda: asyncio.run_coroutine_threadsafe(cron_job(app), app.loop))
    while True:
        schedule.run_pending()
        time.sleep(60)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Text("Scrappe"), scrappe))
    # Start the schedule in a background thread
    threading.Thread(target=run_schedule, args=(app,), daemon=True).start()
    app.run_polling()

if __name__ == "__main__":
    main()