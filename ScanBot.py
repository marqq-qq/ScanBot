import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from io import BytesIO
import pytesseract
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()

# Токен для телеграм бота
TELEGRAM_API_TOKEN = os.getenv("BOT_TOKEN")

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Путь к tesseract (для Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\tesseract'


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Приветствую!\n"
                                    "Я бот для расшифровки текста с изображений\n"
                                    "Присылайте ваше изображение:")


# Обработчик фотографий
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Получаем фото с наибольшим разрешением
        photo_file = await update.message.photo[-1].get_file()

        # Скачиваем фото без сохранения на диск
        photo_bytes = await photo_file.download_as_bytearray()

        # Преобразуем в объект BytesIO для работы с PIL
        image_stream = BytesIO(photo_bytes)

        # Открываем изображение с помощью PIL
        image = Image.open(image_stream)

        # Распознаем текст с помощью Tesseract
        text = pytesseract.image_to_string(image, lang='rus+eng')

        # Отправляем распознанный текст или сообщение о неудаче
        await update.message.reply_text(text if text.strip() else "Не удалось распознать текст на изображении")

    except Exception as e:
        logger.error(f"Ошибка при обработке изображения: {e}")
        await update.message.reply_text("Произошла ошибка при обработке изображения")


async def handle_everything_else(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Простите, но я работаю только с изображениями")


def main():
    # Создаем Application
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.ALL, handle_everything_else))

    # Запускаем бота
    application.run_polling()
    logger.info("Бот запущен")


if __name__ == '__main__':
    main()