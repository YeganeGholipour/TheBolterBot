# Telegram Music Lyrics Bot

A Telegram bot written in Python that sends music lyrics to users every 3 hours.

## Overview

This Telegram bot allows users to receive music lyrics directly within their Telegram chats. The bot automatically sends lyrics for a predefined list of songs every 3 hours, providing users with a steady stream of musical content.

## Features

- **Automatic Lyrics Updates**: The bot fetches the latest lyrics for selected songs from an external source and sends them to users at regular intervals.

- **Customizable Interval**: Users can customize the frequency of lyric updates according to their preferences.

- **User Interaction**: Users can interact with the bot to request lyrics for specific songs or artists.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/telegram-music-lyrics-bot.git
cd telegram-music-lyrics-bot
```
2. Install the required Python packages:
```bash
pip install -r requirements.txt
```
3. Set up a Telegram bot and obtain the API token from the BotFather
4. Replace the placeholder token in the config.py file with your actual bot token
5. Run the bot script:
```bash
python service.py
```
## Usage
Start the bot by sending a message to your Telegram bot.
The bot will automatically send music lyrics every 3 hours.
You can also interact with the bot to request lyrics for specific songs or artists.
Configuration
config.py: Contains configuration parameters such as the Telegram bot token and other settings.
Contributing
Contributions are welcome! If you'd like to contribute to this project, please fork the repository, make your changes, and submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements
This project uses the python-telegram-bot library for interacting with the Telegram Bot API.
Special thanks to Genius for providing the music lyrics data through their API.
