Certainly! Here's the updated `README.md` file in English:

# Telegram Todo Bot

Telegram Todo Bot is a simple Telegram bot designed to help you manage your to-do list. You can add, view, and remove to-do items. Additionally, the bot can generate an image with your to-do list and upload it to Imgur.

## Available Commands

- `/start`: Begin using the bot and receive a welcome message.
- `/todo <text>`: Add a new to-do item with the specified text.
- `/list`: Generate an image with the to-do list and send it to you.
- `/tododel <number>`: Remove a specific to-do item by providing its number.
- `/help`: Display the help message with a summary of available commands.

## Configuration

To configure the bot, follow these steps:

1. Create a new Telegram bot using [BotFather](https://core.telegram.org/bots#botfather).
2. Copy your bot's token.
3. Create a file named `.env` in the same directory as your Python code.
4. Inside the `.env` file, add your bot token, Imgur client ID, and Imgur client secret:

```
TOKEN=INSERT_YOUR_TOKEN_HERE
IMGUR_CLIENT_ID=INSERT_YOUR_CLIENT_ID_HERE
IMGUR_CLIENT_SECRET=INSERT_YOUR_CLIENT_SECRET_HERE
```

## Running the Bot

To run the bot, ensure that you have Python installed on your system. You can run the bot using the following commands:

```bash
pip install -r requirements.txt
python bot.py
```

Make sure to install the necessary dependencies by running `pip install -r requirements.txt`. The bot will listen for commands sent on Telegram and respond accordingly.

Feel free to use the Telegram Todo Bot to stay organized and manage your tasks efficiently.

---

