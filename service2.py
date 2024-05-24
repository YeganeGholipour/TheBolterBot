import os
import random
import psycopg2
from dotenv import load_dotenv, dotenv_values 
import logging
from typing import Final
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackContext

logging.basicConfig(level=logging.INFO)

load_dotenv() 

TOKEN: Final = os.getenv("TOKEN")
CLIENT_ACCESS_TOKEN: Final = os.getenv("CLIENT_ACCESS_TOKEN")


def connect_to_database():
    conn = psycopg2.connect(
        host="localhost",
        database="songscraper",
        user="postgres",
        password="admin"
    )
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM songs")
    songs = cur.fetchone()
    cur.close()

    return songs, conn

def get_lyrics(songs, conn):
    song = random.choice(songs)
    cur = conn.cursor()
    cur.execute(f"SELECT lyrics FROM lyrics WHERE song_name = '{song}'")
    lyrics = cur.fetchone()
    cur.execute(f"SELECT url FROM lyrics WHERE song_name = '{song}'")
    url = cur.fetchone()
    cur.close()
    conn.close()

    return lyrics, song, url
    
# Command handlers
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"/start command is requested by user {update.effective_user.id} ...")
    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = "Welcome to the Bolter Bot :)",
        reply_to_message_id = update.effective_message.id,
        )

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"/help command is requested by user {update.effective_user.id} ...")
    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = """The Botler works in this manner:
        /start --> start the bot
        /help --> see this message
        /lyrics --> You can have a random lyrics from one of Taylor Swift Songs
        /schedule --> see a taylor swift lyrics every hour """,
        reply_to_message_id= update.effective_message.id,
    )


async def send_lyrics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"/lyrics command is requested by user {update.effective_user.id} ...")
    songs, connection = connect_to_database()
    lyrics, song, url = get_lyrics(songs, connection)
    await context.bot.send_message(
        chat_id= update.effective_chat.id,
        text = f"{str(song)}" + "\n" + str(lyrics) + f"\n {str(url)}",
        reply_to_message_id= update.effective_message.id,
    )



# Job queue handlers
async def hourly_artist_lyrics(context: CallbackContext):
    logging.info("Finding lyrics for the scheduled lyrics ....")
    songs, connection = connect_to_database()
    lyrics, song, url = get_lyrics(songs, connection)
    await context.bot.send_message(
        chat_id=1392123839,
        text = f"{str(song)}" + "\n" + str(lyrics) + f"\n {str(url)}",
    )

async def start_job_handler(update: Update, context:ContextTypes.DEFAULT_TYPE):
    context.job_queue.run_repeating(hourly_artist_lyrics, interval=30, first=0)
    await update.message.reply_text("Job started successfully!")


if __name__ == "__main__":
    bot = ApplicationBuilder().token(TOKEN).build()
    job_queue = bot.job_queue
    logging.info("Application is starting ...")
    bot.add_handler(CommandHandler("start", start_handler))
    bot.add_handler(CommandHandler("help", help_handler))
    bot.add_handler(CommandHandler("lyrics", send_lyrics))
    bot.add_handler(CommandHandler("startjob", start_job_handler))
    bot.run_polling()
