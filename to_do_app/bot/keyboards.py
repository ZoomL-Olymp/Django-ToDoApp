from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Создаем клавиатуру
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="/list"),
            KeyboardButton(text="/add"),
        ],
        [
            KeyboardButton(text="/done"),
            KeyboardButton(text="/delete"),
        ],
        [
            KeyboardButton(text="/help"),
            KeyboardButton(text="/logout"),
        ]
    ],
    resize_keyboard=True,  # Делаем клавиатуру меньше
    one_time_keyboard=False,  # Клавиатура не скрывается после нажатия
    input_field_placeholder="Выберите действие",  # Текст в поле ввода
    selective=True, # Для каких пользователей клавиатура
)