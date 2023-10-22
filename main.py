import telebot
import requests
import pyimgur
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from dotenv import dotenv_values, set_key
from webcolors import name_to_hex
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

# Initialize colors from .env
background_color = env_data.get('BACKGROUND_COLOR')
title_color = env_data.get('TITLE_COLOR')
text_color = env_data.get('TEXT_COLOR')

# Command /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome! Use /todo to add a new todo, /list to generate an image with todos, or /tododel <number> to remove a todo.")

# Comando /setbackgroundcolor

@bot.message_handler(commands=['setbackgroundcolor'])
def set_background_color(message):
    user_id = message.from_user.id
    color_name = message.text.split(' ', 1)[1]
    try:
        global background_color
        background_color = name_to_hex(color_name)
        write_colors_to_env(background_color, title_color, text_color)  # Aggiorna il file .env
        bot.reply_to(message, f"Background color set to {color_name} ({background_color})")
    except ValueError:
        bot.reply_to(message, f"Invalid color name. Please use a valid color name like 'blue', 'red', etc.")

# Comando /settitlecolor
@bot.message_handler(commands=['settitlecolor'])
def set_title_color(message):
    user_id = message.from_user.id
    color_name = message.text.split(' ', 1)[1]
    try:
        global title_color
        title_color = name_to_hex(color_name)
        write_colors_to_env(background_color, title_color, text_color)  # Aggiorna il file .env
        bot.reply_to(message, f"Title color set to {color_name} ({title_color})")
    except ValueError:
        bot.reply_to(message, f"Invalid color name. Please use a valid color name like 'blue', 'red', etc.")

# Comando /settextcolor
@bot.message_handler(commands=['settextcolor'])
def set_text_color(message):
    user_id = message.from_user.id
    color_name = message.text.split(' ', 1)[1]
    try:
        global text_color
        text_color = name_to_hex(color_name)
        write_colors_to_env(background_color, title_color, text_color)  # Aggiorna il file .env
        bot.reply_to(message, f"Text color set to {color_name} ({text_color})")
    except ValueError:
        bot.reply_to(message, f"Invalid color name. Please use a valid color name like 'blue', 'red', etc.")


# Comando /todo
@bot.message_handler(commands=['todo'])
def add_todo(message):
    todo_text = message.text.split('/todo', 1)
    if len(todo_text) > 1:
        todo_text = todo_text[1].strip()
        if todo_text and todo_text != '/':
            with open(TODO_FILE, 'r') as file:
                lines = file.readlines()

            # Trova il numero più alto nei todo esistenti
            existing_numbers = [int(line.split('.')[0].strip()) for line in lines if line.strip() and line[0].isdigit()]
            new_number = max(existing_numbers) + 1 if existing_numbers else 1

            # Wrap del testo se è troppo lungo
            max_line_length = 50  # Imposta la lunghezza massima della linea
            wrapped_todo = textwrap.fill(todo_text, width=max_line_length)

            formatted_todo = f"{new_number}. {wrapped_todo}\n"

            with open(TODO_FILE, 'a') as file:
                file.write(formatted_todo)
            bot.reply_to(message, f"Todo added: {wrapped_todo}")
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
        image = create_image_with_todos(todos)
        if image:
            # Invia le immagini come messaggio

            image_bytes = BytesIO()
            image.save(image_bytes, format='PNG')
            image_bytes.seek(0)
            bot.send_photo(message.chat.id, photo=image_bytes)
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
            deleted_todo = todos.pop(todo_number - 1)

            with open(TODO_FILE, 'w') as file:
                file.writelines(todos)

            bot.reply_to(message, f"Todo removed: {deleted_todo.strip()}")
        else:
            bot.reply_to(message, "Invalid todo number. Use /del followed by a valid number.")
    except ValueError:
        bot.reply_to(message, "Use /del followed by a valid number.")
    except FileNotFoundError:
        bot.reply_to(message, "Todo file not found. Use /todo to add todos.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred while removing the todo: {str(e)}")


# Comando /clear
@bot.message_handler(commands=['clear'])
def clear_todos(message):
    try:
        with open(TODO_FILE, 'w') as file:
            file.truncate(0)  # Svuota il file
        bot.reply_to(message, "All todos have been cleared.")
    except FileNotFoundError:
        bot.reply_to(message, "The todo file was not found.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred while clearing todos: {str(e)}")


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

def write_colors_to_env(background, title, text):
    env_path = '.env'
    with open(env_path, 'r') as file:
        lines = file.readlines()

    for i in range(len(lines)):
        if lines[i].startswith('BACKGROUND_COLOR='):
            lines[i] = f'BACKGROUND_COLOR={background}\n'
        elif lines[i].startswith('TITLE_COLOR='):
            lines[i] = f'TITLE_COLOR={title}\n'
        elif lines[i].startswith('TEXT_COLOR='):
            lines[i] = f'TEXT_COLOR={text}\n'

    with open(env_path, 'w') as file:
        file.writelines(lines)

def create_image_with_todos(text):
    # Crea un oggetto ImageFont per il calcolo delle dimensioni del testo
    try:
        font = ImageFont.truetype("JetBrainsMonoNLNerdFont-Regular.ttf", size=24)
    except IOError:
        font = ImageFont.load_default()

    # Calcola le dimensioni del testo
    max_line_width = max(font.getsize(line)[0] for line in text.split("\n"))
    line_height = font.getsize("A")[1]

    # Imposta la larghezza fissa dell'immagine
    image_width = 800  # Larghezza fissa

    # Suddividi il testo in linee separate
    lines = text.strip().split('\n')

    # Calcola l'altezza necessaria in base al numero di righe di testo
    image_height = 100 + line_height * len(lines)

    # Crea un'immagine vuota con sfondo colorato
    image = Image.new("RGB", (image_width, image_height), background_color)

    # Crea un oggetto ImageDraw per disegnare il testo sull'immagine
    draw = ImageDraw.Draw(image)

    # Disegna il titolo "TODO"
    title_position = (50, 25)
    title = "TODO"
    draw.text(title_position, title, fill=title_color, font=font)

    # Disegna le righe di testo
    text_position = (50, 75)
    for line in lines:
        wrapped_lines = textwrap.wrap(line, width=int(image_width - 100))
        for wrapped_line in wrapped_lines:
            draw.text(text_position, wrapped_line, fill=text_color, font=font)
            text_position = (text_position[0], text_position[1] + line_height)

    return image

# Run the bot
if __name__ == "__main__":
    bot.polling()
