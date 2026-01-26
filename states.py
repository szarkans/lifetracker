from aiogram.fsm.state import StatesGroup, State

class Survey(StatesGroup):
    name = State()
    rate_type = State()

class Rating(StatesGroup):
    choose_day = State()
    rate = State()
    note = State()
    confirm = State()
