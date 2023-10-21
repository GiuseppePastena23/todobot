import telebot
import requests
import pyimgur
from PIL import Image
import os
import io
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Read the Telegram token from the .env file
TOKEN = os.getenv('TOKEN')
IMGUR_CLIENT_ID = os.getenv('IMGUR_CLIENT_ID')
IMGUR_CLIENT_SECRET = os.getenv('IMGUR_CLIENT_SECRET')

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
        formatted_message = f"```\n{todos}\n```"
        bot.reply_to(message, "Generating an image with your todo list...")

        # Create an image with Carbon
        carbon_url = create_carbon_image(todos)
        if carbon_url:
            image = requests.get(carbon_url)
            image_buffer = io.BytesIO(image.content)
            image_buffer.name = "todo.png"

            # Send the image to the user
            bot.send_photo(message.chat.id, image_buffer)
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

# Function to create an image with Carbon
# Function to create an image with Carbon
def create_carbon_image(code):
    carbon_url = None
    try:
        carbon_api_url = 'https://carbonara.vercel.app/api/cook'
        payload = {
            'code': code,
            'backgroundColor': 'rgba(255,255,255,1)',
            't': 'material',
        }
        response = requests.post(carbon_api_url, json=payload)
        if response.status_code == 200:
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))
            img.save('carbon.png')

            im = pyimgur.Imgur(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET)
            uploaded_image = im.upload_image('carbon.png', title="Todo List")
            carbon_url = uploaded_image.link
        else:
            print("Carbon service returned status code:", response.status_code)
    except Exception as e:
        print("Error creating a Carbon image:", str(e))
    return carbon_url




# Run the bot
if __name__ == "__main__":
    bot.polling()