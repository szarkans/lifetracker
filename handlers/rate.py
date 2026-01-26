from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

from handlers.start import command_start_handler, start_survey
from keyboards import main_keyboard
from states import Rating
from database import async_session
from sqlalchemy import select
from models import User, Rates

from datetime import datetime, date, timedelta

rate_router = Router()

@rate_router.message(F.text == "⭐️ Оценить день")
async def choose_day_of_rating(message: Message, state: FSMContext) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
    if user:
        await state.set_state(Rating.choose_day)
        await message.answer("Какой день оценим?", reply_markup=ReplyKeyboardMarkup(
            keyboard=[[
                KeyboardButton(text="Сегодня"),
                KeyboardButton(text="Вчера")
            ]],
            resize_keyboard=True
        ))
    else:
        await message.answer("Ох, я не нашла тебя в базе данных... Познакомимся?")
        await start_survey(message, state)

@rate_router.message(Rating.choose_day, F.text.in_(["Сегодня", "Вчера"]))
async def rate_day(message: Message, state: FSMContext) -> None:
    await state.update_data(day=message.text)
    await state.set_state(Rating.rate)

    await message.answer("Как прошёл твой день?", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="1"),
                KeyboardButton(text="2"),
                KeyboardButton(text="3"),
                KeyboardButton(text="4"),
                KeyboardButton(text="5"),
            ]
        ],
        resize_keyboard=True
    ))

@rate_router.message(Rating.choose_day)
async def invalid_rate_day(message: Message) -> None:
    await message.answer("К сожалению пока что можно выбрать лишь ''Сегодня'' или ''Вчера''. Выбери их на клавиатуре.")

@rate_router.message(Rating.rate, F.text.in_(["1","2","3","4","5"]))
async def take_note(message: Message, state: FSMContext) -> None:
    await state.update_data(rate=message.text)
    print(message.text)
    if message.text in ["1", "2"]:
        await message.answer("Ничего, завтра всё будет лучше.")
    await state.set_state(Rating.note)
    await message.answer("Напиши как прошёл твой день, если хочешь конечно.", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Не хочу")
            ]
        ],
        resize_keyboard=True
    ))

@rate_router.message(Rating.rate)
async def invalid_take_note(message: Message) -> None:
    await message.answer("К сожалению, пока что день можно оценить только по пятибальной шкале. "
                         "Выбери оценку дня на клавиатуре.")

@rate_router.message(Rating.note)
async def confirm_rating(message: Message, state: FSMContext) -> None:
    print(message.text)
    await state.set_state(Rating.confirm)
    if message.text == "Не хочу":
        await message.answer("Без проблем.")
        await state.update_data(note="#NONOTE")
    else:
        await state.update_data(note=message.text)
    data = await state.get_data()
    await message.answer(f"Твоя оценка дня: <b>{data.get('rate')}</b>\n\n"
                         f""
                         f"Твоя запись дня:\n"
                         f"<blockquote>{data.get('note') if data.get('note') != '#NONOTE' else 'Записи нет.'}</blockquote>\n\n"
                         f"Всё правильно?", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Да, всё верно"),
                KeyboardButton(text="Нет, начать заново")
            ]
        ],
        resize_keyboard=True
    ))

@rate_router.message(Rating.confirm)
async def confirmation(message: Message, state: FSMContext) -> None:
    if message.text == "Да, всё верно":
        data = await state.get_data()
        await state.clear()
        print(data)
        async with async_session() as session:
            new_note = Rates(
                tg_id=message.from_user.id,
                note=data.get("note"),
                rate=int(data.get("rate")),
                rate_date=date.today() if data.get("day") == "Сегодня" else (date.today() - timedelta(days=1))
            )
            session.add(new_note)
            await session.commit()
        await message.answer("Записал твой день. Отдыхай :)", reply_markup=main_keyboard())
    elif message.text == "Нет, начать заново":
        # Вот она, магия: просто вызываем стартовую функцию!
        await choose_day_of_rating(message, state)
    else:
        await message.answer("Пожалуйста, воспользуйся кнопками.", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Да, всё верно"),
                KeyboardButton(text="Нет, начать заново")
            ]
        ],
        resize_keyboard=True
    ))

