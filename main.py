import telebot
import requests
import pyimgur
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
from dotenv import dotenv_values
import textwrap

# Load environment variables from the .env file
env_path = '.env'
env_data = dotenv_values(env_path)

# Read the Telegram token from the .env file
BOT_TOKEN = env_data['TOKEN']


# Create a bot instance
bot = telebot.TeleBot(BOT_TOKEN)

# Name of the file to store todos
TODO_FILE = "todo.md"

# Command /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome! Use /todo to add a new todo, /list to generate an image with todos, or /tododel <number> to remove a todo.")

# Comando /todo
# Comando /todo
@bot.message_handler(commands=['todo'])
def add_todo(message):
    todo_text = message.text.split('/todo', 1)
    if len(todo_text) > 1:
        todo_text = todo_text[1].strip()
        if todo_text:
            with open(TODO_FILE, 'r') as file:
                lines = file.readlines()
            
            # Calcola il numero da aggiungere (l'ultimo numero nella lista + 1)
            if lines:
                last_line = lines[-1]
                last_number = int(last_line.split(' ', 1)[0].strip())
                new_number = last_number + 1
            else:
                new_number = 1
            
            formatted_todo = f"{new_number}. {todo_text}\n"
            
            with open(TODO_FILE, 'a') as file:
                file.write(formatted_todo)
            bot.reply_to(message, f"Todo added: {formatted_todo}")
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
@bot.message_handler(commands=['del'])
def remove_todo(message):
    try:
        todo_number = int(message.text.replace('/del ', '').strip())
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
        bot.reply_to(message, "Use /del followed by a valid number.")

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
- `/del <number>`: Remove a specific to-do item based on its number.
- `/help`: Display this help message.

Feel free to use these commands to stay organized and manage your tasks. Enjoy using the bot!
    """
    bot.reply_to(message, help_message, parse_mode="Markdown")


# Function to create a customized image with adjusted width and word wrap
def create_image_with_text(text):
    try:
        # Calculate image size based on text length
        max_image_width = 1000  # Maximum width
        max_image_height = len(text) * 10 # Maximum height

        # Create an image with a custom background color (grayish)
        img = Image.new('RGB', (max_image_width, max_image_height), color='#1a1717')  # Grayish background

        # Create a drawing context
        d = ImageDraw.Draw(img)

        # Use a custom font (you can provide the path to a specific font file)
        font = ImageFont.truetype("JetBrainsMonoNLNerdFont-Regular.ttf", 20)  # Replace with the path to your custom font file

        # Text colors
        title_color = '#FF5733'  # Title "TODO" color (orange)
        todo_color = '#1E8449'   # Todo text color (green)

        # Format the text as bold (Markdown-style)
        text = text.replace('**', '')  # Remove existing bold formatting (if any)
        text = text.replace('*', '**')  # Apply Markdown-style bold formatting

        # Calculate the image width based on the longest line
        text_width = max(font.getsize(line)[0] for line in text.split('\n'))

        # Ensure the image width doesn't exceed the maximum
        image_width = min(text_width, max_image_width)

        # Create a new image with the adjusted dimensions
        img = Image.new('RGB', (image_width, max_image_height), color='#1a1717')

        # Create a drawing context for the new image
        d = ImageDraw.Draw(img)

        # Draw the title "TODO" in orange
        d.text((10, 10), "TODO", font=font, fill=title_color)

        # Split and wrap text into lines with word wrap
        lines = text.split('\n')
        y = 40
        for line in lines:
            wrapped_lines = textwrap.wrap(line, width=40)  # Adjust the width as needed
            for wrapped_line in wrapped_lines:
                d.text((10, y), wrapped_line, font=font, fill=todo_color)
                y += font.getsize(wrapped_line)[1]

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
