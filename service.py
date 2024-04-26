import os
from dotenv import load_dotenv, dotenv_values 
import logging
import random
import requests
from typing import Final
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackContext

logging.basicConfig(level=logging.INFO)

load_dotenv() 

TOKEN: Final = os.getenv("TOKEN")
CLIENT_ACCESS_TOKEN: Final = os.getenv("CLIENT_ACCESS_TOKEN")

def get_artist_id(artist_name):
    search_term = artist_name
    genius_search_url = "http://api.genius.com/search"
    params = {"q": search_term, "access_token": CLIENT_ACCESS_TOKEN}

    response = requests.get(genius_search_url, params=params).json()

    if response["meta"]["status"] == 200:
        artist_id = response["response"]["hits"][0]["result"]["primary_artist"]["id"]
        return artist_id
    

def get_song_id(artist_id):
    genius_search_url = f"http://api.genius.com/artists/{artist_id}/songs"
    params = {"access_token": CLIENT_ACCESS_TOKEN}

    response = requests.get(genius_search_url, params=params).json()
    if response["meta"]["status"] == 200:
        songs = response["response"]["songs"]
        random_song = random.choice(songs)
        song_id = random_song["id"]
        return song_id


def get_referents(song_id):
    genius_search_url = f"http://api.genius.com/referents?song_id={song_id}"
    params = {"access_token": CLIENT_ACCESS_TOKEN}
    response = requests.get(genius_search_url, params=params).json()

    logging.info("Genius API Response: %s", response)

    if response["meta"]["status"] == 200:
        referents = response["response"]["referents"]
        return referents

def get_lyrics(referents):
    referent = random.choice(referents)
    lyrics = referent["fragment"]

    url = referent["url"]
    
    return (lyrics, url)

def lyrics_builder(artist):
    
    logging.info("Getting artist id ...")
    artist_id = get_artist_id(artist)

    logging.info(f"artist id is: {artist_id}")

    logging.info("Getting song id ...")
    song_id = get_song_id(artist_id)
    logging.info(f"song id is: {song_id}")

    logging.info("Getting all the referents ...")
    referents = get_referents(song_id)
    logging.info(f"referents is: {referents}")

    if len(referents)==0:
        lyrics_builder(artist)

    logging.info("Getting a random lyrics ...")
    lyrics, url = get_lyrics(referents)
    return lyrics, url
    
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
        /artist --> You give us the name of the artist you want a lyrics of
        /schedule --> see a taylor swift lyrics every hour """,
        reply_to_message_id= update.effective_message.id,
    )

async def artist_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"/artist_name command is requested by user {update.effective_user.id} ...")

    artist = " ".join(context.args)
    if len(artist)>0:
        await context.bot.send_message(
            chat_id= update.effective_chat.id,
            text = "Ok, The Bolter will find a lyrics about: " + artist,
            reply_to_message_id= update.effective_message.id,
        )

        lyrics, url = lyrics_builder(artist)

        logging.info("Sending the lyrics ...")
        await context.bot.send_message(
            chat_id= update.effective_chat.id,
            text = lyrics + f"\n {url}",
            reply_to_message_id= update.effective_message.id,
        )
        logging.info("Lyrics sent successfully ...")

    else:
        await context.bot.send_message(
            chat_id= update.effective_chat.id,
            text = "You need to give us the name of the artist... ",
            reply_to_message_id= update.effective_message.id,
        )

# Job queue handlers
async def hourly_artist_lyrics(context: CallbackContext):
    logging.info("Finding lyrics for the scheduled lyrics ....")
    lyrics, url =  lyrics_builder("taylor swift")  
    await context.bot.send_message(
        chat_id=1392123839,
        text=lyrics + f"\n {url}"
    )

async def start_job_handler(update: Update, context:ContextTypes.DEFAULT_TYPE):
    context.job_queue.run_repeating(hourly_artist_lyrics, interval=30, first=0)
    await update.message.reply_text("Job started successfully!")


# # error handlers
# async def artist_error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     logging.error("The context is empty. The user has not entered a name")



if __name__ == "__main__":
    bot = ApplicationBuilder().token(TOKEN).build()
    job_queue = bot.job_queue
    logging.info("Application is starting ...")
    bot.add_handler(CommandHandler("start", start_handler))
    bot.add_handler(CommandHandler("help", help_handler))
    bot.add_handler(CommandHandler("artist", artist_name_handler))
    bot.add_handler(CommandHandler("startjob", start_job_handler))
    # bot.add_error_handler(artist_error_handler)
    bot.run_polling()
