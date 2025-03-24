from aiogram.fsm.state import StatesGroup, State

class TaskDialog(StatesGroup):
    title = State()
    description = State()
    due_date = State()
    category = State()