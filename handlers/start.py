from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton

from keyboards import main_keyboard
from states import Survey
from database import async_session
from sqlalchemy import select
from models import User

start_router = Router()

@start_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """
    /start
    """
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
        if user:
            await message.answer("Ты хочешь начать всё с нуля?")
        else:
            await start_survey(message, state)

async def start_survey(message: Message, state: FSMContext):
    await state.set_state(Survey.name)
    await message.answer(
        f"Привет. Это - <b>DailyFeels</b>, твой личный, <b>анонимный</b> и бесплатный трекер настроения.\n "
        f"Здесь ты можешь оценивать проведённый день и следить как проходит твоя неделя, месяц или год.\n\n"
        f"Как я могу тебя называть? Если не хочешь указывать имя - нажми кнопку на клавиатуре.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Не хочу называть.")
                ],
            ],
            resize_keyboard=True,
        ))

@start_router.message(Survey.name)
async def process_name(message: Message, state: FSMContext) -> None:
    print(message.text)
    if message.text == "Не хочу называть.":
        await state.update_data(name="#NONAME")
        await message.answer("Без проблем, я запишу твоё имя из телеграма!")
    else:
        await state.update_data(name=message.text)
    await state.set_state(Survey.rate_type)
    await message.answer("Как ты бы хотел(а) оценивать свой день?\n\n"
                         "5 баллов, более просто\n"
                         "1 - отвратительный день\n"
                         "5 - замечательный день"
                         "\n\n"
                         "или"
                         "\n\n"
                         "10 баллов, более точно\n"
                         "1 - отвратительный день\n"
                         "5 - обычный день, ни туда, ни сюда\n"
                         "10 - замечательный день",
                         reply_markup=ReplyKeyboardMarkup(
                             keyboard=[
                                 [
                                     KeyboardButton(text="5"),
                                     KeyboardButton(text="10")
                                 ],
                             ],
                             resize_keyboard=True
                         ))

@start_router.message(Survey.rate_type)
async def rate_choosen(message: Message, state: FSMContext) -> None:
    await state.update_data(rate_type=message.text)
    data = await state.get_data()
    name = data.get("name")
    print(data)
    await state.clear()
    await message.answer(text=f"Чудесно, {name}! Начнём?" if name != "#NONAME" else "Чудесно. Начнём?",
                         reply_markup=main_keyboard())
    async with async_session() as session:
        new_user = User(
            tg_id = message.from_user.id,
            name=name,
            scale=int(data.get("rate_type"))
        )
        session.add(new_user)
        await session.commit()
