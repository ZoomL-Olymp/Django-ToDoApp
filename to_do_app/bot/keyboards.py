from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

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
            KeyboardButton(text="/createcategory"),
        ]
    ],
    resize_keyboard=True,  # Делаем клавиатуру меньше
    one_time_keyboard=False,  # Клавиатура не скрывается после нажатия
    input_field_placeholder="Выберите действие",  # Текст в поле ввода
    selective=True, # Для каких пользователей клавиатура
)

def categories_keyboard(categories: list) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру со списком категорий."""
    keyboard = []
    for category in categories:
        keyboard.append(
            [InlineKeyboardButton(text=category['name'], callback_data=f"category_{category['id']}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)