print("Код начинается!")
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import requests

# Настраиваем логи
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токены
TELEGRAM_TOKEN = "7933835023:AAF7aDAPivnA4E_Xg_YFK7zU3aZ5WBNFurE"  # Замени на новый токен от BotFather
WEATHER_API_KEY = "baea9bd7ebacfad58cbc6f31a1e1bda0"
print("Токены загружены!")

# Создаём бота
bot = Bot(token=TELEGRAM_TOKEN)
print("Бот создан!")

# Создаём диспетчер
dp = Dispatcher()
print("Диспетчер создан!")

# Клавиатура с кнопками
main_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="Погода"), types.KeyboardButton(text="Помощь")]
    ],
    resize_keyboard=True
)

# Определяем состояния для цепочки сообщений (FSM)
class WeatherFlow(StatesGroup):
    waiting_for_city = State()

# Функция для получения погоды
def get_weather(city: str) -> str:
    """Получает погоду для города через API OpenWeatherMap."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    try:
        response = requests.get(url)
        data = response.json()
        temp = data["main"]["temp"]
        return f"В {city} сейчас {temp}°C"
    except Exception as e:
        logger.error(f"Ошибка при запросе погоды: {e}")
        return f"Не могу найти {city}. Попробуй ещё раз!"

# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Приветствие и показ клавиатуры."""
    logger.info(f"Получена команда /start от {message.from_user.id}")
    await message.reply("Привет! Я бот погоды. Выбери 'Погода' или 'Помощь'.", reply_markup=main_keyboard)

# Обработчик кнопки "Погода"
@dp.message(lambda message: message.text.lower() == "погода")
async def weather_request(message: types.Message, state: FSMContext):
    """Запускает цепочку: просит ввести город."""
    logger.info(f"Получен запрос 'Погода' от {message.from_user.id}")
    await message.reply("Какой город тебя интересует?")
    await state.set_state(WeatherFlow.waiting_for_city)

# Обработчик ввода города
@dp.message(WeatherFlow.waiting_for_city)
async def process_city(message: types.Message, state: FSMContext):
    """Обрабатывает город и завершает цепочку."""
    city = message.text.strip()
    logger.info(f"Получен город '{city}' от {message.from_user.id}")
    weather_info = get_weather(city)
    await message.reply(weather_info, reply_markup=main_keyboard)
    await state.clear()

# Обработчик кнопки "Помощь"
@dp.message(lambda message: message.text.lower() == "помощь")
async def help_command(message: types.Message):
    """Показывает инструкцию."""
    logger.info(f"Получен запрос 'Помощь' от {message.from_user.id}")
    await message.reply("Нажми 'Погода', введи город, и я покажу температуру!", reply_markup=main_keyboard)

# Запуск бота
async def main():
    """Запускает бота."""
    print("Бот запущен!")
    logger.info("Бот начал polling")
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("Доходим до main!")
    asyncio.run(main())