from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.api_client import create_category
from bot.utils import UserData
from bot.keyboards import main_keyboard


router = Router()

class CreateCategory(StatesGroup):
    waiting_for_name = State()

@router.message(F.text == "/createcategory")
async def create_category_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    access_token, _ = await UserData.get_tokens(user_id)
    if not access_token:
        await message.answer("Вы не авторизованы. Используйте /start")
        return

    await message.answer("Введите название новой категории:", reply_markup=main_keyboard) # Add keyboard
    await state.set_state(CreateCategory.waiting_for_name)


@router.message(CreateCategory.waiting_for_name)
async def create_category_name(message: Message, state: FSMContext):
    category_name = message.text
    user_id = message.from_user.id
    access_token, _ = await UserData.get_tokens(user_id)
    if not access_token:
        await message.answer("Вы не авторизованы")
        await state.clear()
        return

    result = await create_category(access_token, category_name)

    if result:
         await message.answer(f"Категория '{category_name}' создана! (ID: {result.get('id')})", reply_markup=main_keyboard) # Show ID
    else:
        await message.answer("Не удалось создать категорию.  Попробуйте еще раз.", reply_markup=main_keyboard)

    await state.clear()