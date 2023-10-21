import telebot
import requests
import pyimgur
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Read the Telegram token from the .env file
TOKEN = os.getenv('TOKEN')


# Create a bot instance
bot = telebot.TeleBot(TOKEN)

# Name of the file to store todos
TODO_FILE = "todo.md"

# Command /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome! Use /todo to add a new todo, /list to generate an image with todos, or /tododel <number> to remove a todo.")

# Comando /todo
@bot.message_handler(commands=['todo'])
def add_todo(message):
    todo_text = message.text.split('/todo', 1)
    if len(todo_text) > 1:
        todo_text = todo_text[1].strip()
        if todo_text:
            with open(TODO_FILE, 'a') as file:
                file.write(f"- {todo_text}\n")
            bot.reply_to(message, f"Todo added: {todo_text}")
        else:
            bot.reply_to(message, "You must specify the todo text. For example: /todo Buy groceries.")
    else:
        bot.reply_to(message, "You must specify the todo text. For example: /todo Buy groceries.")


# Comando /list
@bot.message_handler(commands=['list'])
def list_todo(message):
    with open(TODO_FILE, 'r') as file:
        todos = file.read()
    if todos:
        image = create_image_with_text(todos)
        if image:
            bot.send_photo(message.chat.id, image)
        else:
            bot.reply_to(message, "Unable to generate the image with your todo list.")
    else:
        bot.reply_to(message, "No todos present.")

# Command /tododel
@bot.message_handler(commands=['tododel'])
def remove_todo(message):
    try:
        todo_number = int(message.text.replace('/tododel ', '').strip())
        with open(TODO_FILE, 'r') as file:
            todos = file.readlines()
        if 1 <= todo_number <= len(todos):
            del todos[todo_number - 1]
            with open(TODO_FILE, 'w') as file:
                file.writelines(todos)
            bot.reply_to(message, f"Todo number {todo_number} removed.")
        else:
            bot.reply_to(message, "Invalid todo number.")
    except ValueError:
        bot.reply_to(message, "Use /tododel followed by a valid number.")

# Comando /clear
@bot.message_handler(commands=['clear'])
def clear_todos(message):
    try:
        with open(TODO_FILE, 'w') as file:
            file.truncate(0)  # Svuota il file
        bot.reply_to(message, "All todos have been cleared.")
    except Exception as e:
        bot.reply_to(message, "An error occurred while clearing todos.")


# Command /help
@bot.message_handler(commands=['help'])
def help(message):
    help_message = """**Telegram Todo Bot Help**

This bot allows you to manage your to-do list. Here are the available commands:

- `/start`: Start the bot and receive a welcome message.
- `/todo <text>`: Add a new to-do item with the specified text.
- `/list`: Generate an image with the list of to-do items and send it.
- `/tododel <number>`: Remove a specific to-do item based on its number.
- `/help`: Display this help message.

Feel free to use these commands to stay organized and manage your tasks. Enjoy using the bot!
    """
    bot.reply_to(message, help_message, parse_mode="Markdown")

# Function to create a customized image with bold text (Markdown-style)
def create_image_with_text(text):
    try:
        # Calculate image size based on text length
        image_width = 600  # Minimum width
        image_height = max(400, len(text) * 10)  # Adjust height based on text length

        # Create an image with a custom background color (grayish)
        img = Image.new('RGB', (image_width, image_height), color='#1a1717')  # Grayish background

        # Create a drawing context
        d = ImageDraw.Draw(img)

        # Use a custom font (you can provide the path to a specific font file)
        font = ImageFont.truetype("arial.ttf", 20)  # Replace with the path to your custom font file

        # Text colors
        title_color = '#FF5733'  # Title "TODO" color (orange)
        todo_color = '#1E8449'   # Todo text color (green)

        # Format the text as bold (Markdown-style)
        text = text.replace('**', '')  # Remove existing bold formatting (if any)
        text = text.replace('*', '**')  # Apply Markdown-style bold formatting

        # Draw text on the image with Markdown-style formatting
        d.text((10, 10), "TODO", font=font, fill=title_color)
        d.text((10, 40), text, font=font, fill=todo_color)

        # Save the image to a BytesIO buffer
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes

    except Exception as e:
        print("Error creating the image:", str(e))
        return None

# Run the bot
if __name__ == "__main__":
    bot.polling()