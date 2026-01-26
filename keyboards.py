from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="⭐️ Оценить день"),
                KeyboardButton(text="👤 Профиль")
            ],
            [
                KeyboardButton(text="🆘 Помощь"),
                KeyboardButton(text="📔 Записи")
            ]
        ],
    resize_keyboard=True)
    return keyboard