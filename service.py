import logging
import random
import requests
from typing import Final
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackContext

logging.basicConfig(level=logging.INFO)

TOKEN: Final = "6896491676:AAE7GFgoAL8H0iAvg148WTWV_66lRJXpNRg"
client_access_token: Final = "stewQW4cPkDNvMOdNut9F9t0p6CqNTi-gIjVEaKOW4V27qHnNchCDZBDTCZ9-MDX"

def get_artist_id(artist_name):
    search_term = artist_name
    genius_search_url = "http://api.genius.com/search"
    params = {"q": search_term, "access_token": client_access_token}

    response = requests.get(genius_search_url, params=params).json()

    if response["meta"]["status"] == 200:
        artist_id = response["response"]["hits"][0]["result"]["primary_artist"]["id"]
        return artist_id
    

def get_song_id(artist_id):
    genius_search_url = f"http://api.genius.com/artists/{artist_id}/songs"
    params = {"access_token": client_access_token}

    response = requests.get(genius_search_url, params=params).json()
    if response["meta"]["status"] == 200:
        songs = response["response"]["songs"]
        random_song = random.choice(songs)
        song_id = random_song["id"]
        return song_id


def get_referents(song_id):
    genius_search_url = f"http://api.genius.com/referents?song_id={song_id}"
    params = {"access_token": client_access_token}
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

def lyrics_builder(artist="taylor swift"):
    logging.info("Getting artist id ...")
    if artist == "taylor swift":
        song_id = get_song_id(1177)
        logging.info("Getting all the referents ...")
        logging.info(f"song id is: {song_id}")
        referents = get_referents(song_id)
        logging.info("Getting a random lyrics ...")
        logging.info(f"referents is: {referents}")
        if len(referents)==0:
            lyrics_builder()
        lyrics, url = get_lyrics(referents)
        return lyrics, url
    else:
        artist_id = get_artist_id(artist)
        logging.info("Getting song id ...")
        logging.info(f"artist id is: {artist_id}")
        song_id = get_song_id(artist_id)
        logging.info("Getting all the referents ...")
        logging.info(f"song id is: {song_id}")
        referents = get_referents(song_id)
        logging.info("Getting a random lyrics ...")
        logging.info(f"referents is: {referents}")
        if len(referents)==0:
            lyrics_builder()
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
    lyrics, url =  lyrics_builder()  
    await context.bot.send_message(
        chat_id=1392123839,
        text=lyrics + f"\n {url}"
    )




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
    # bot.add_error_handler(artist_error_handler)
    job_queue.run_repeating(hourly_artist_lyrics, interval=30, first=0)
    bot.run_polling()
