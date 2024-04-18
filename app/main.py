"""entrypoint"""

import os
import logging
import uuid
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from app.core.faker import Dickfake
from app.datalayer.schemas import NotEyesException

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)
dickfake = Dickfake()


def start(update: Update, context) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_text(f'Привет, {user["first_name"]}! Меня зовут DickFake. \
Отправь мне фото себя или своего друга \
и я заменю на нем глаза и нос на 🍆. На фото может быть \
несколько людей, но лица должны быть крупным \
или средним планом, т.к я элитный бот и \
не имею дел с "корнишончиками" 🥒.')


def help_command(update: Update, context) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("Пришли фотографию, чтобы я натянул на нее писю")


def echo(update: Update, context) -> None:
    """Echo the user message."""
    update.message.reply_text("Отправь фото и увидишь 🍆 на лице")


def build_dickfake(update: Update, context) -> None:
    file = update.message.photo[-1].get_file()
    filename = str(uuid.uuid4().hex) + ".jpg"
    inbox_file_path = os.path.join("/home/bot/inbox_images", filename)
    file.download(inbox_file_path)
    try:
        sent_path = dickfake(filename)
        context.bot.send_photo(chat_id=update.message['chat']['id'],
                               photo=open(sent_path, 'rb'))
        os.remove(sent_path)
    except NotEyesException:
        update.message.reply_text("Не нашел глаз на фото, попробуй прислать фото крупнее")

    except Exception as e:
        print("Error", e)
        update.message.reply_text("Сорян, я заболел((")

    finally:
        os.remove(inbox_file_path)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    if not os.path.exists("/home/bot/inbox_images"):
        os.makedirs("/home/bot/inbox_images")

    if not os.path.exists("/home/bot/sent_images"):
        os.makedirs("/home/bot/sent_images")

    token = os.getenv("bot_token")
    application = Updater(token, use_context=True)

    dp = application.dispatcher
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dp.add_handler(MessageHandler(Filters.photo & ~Filters.command,
                                  build_dickfake))
    # Run the bot until the user presses Ctrl-C
    application.start_polling()
    application.idle()


if __name__ == "__main__":
    main()
