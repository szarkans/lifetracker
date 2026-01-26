from datetime import datetime

from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from keyboards import main_keyboard
from states import Survey
from database import async_session
from sqlalchemy import select, func
from models import User, Rates

generic_router = Router()

@generic_router.message(F.text == "👤 Профиль")
async def profile_button(message: Message, state: FSMContext):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
        query = select(func.count()).select_from(Rates).where(Rates.tg_id == message.from_user.id)
        total_notes = await session.scalar(query) or 0
    date = user.registration_date
    name = user.name
    name = message.from_user.full_name if name == "#NONAME" else name
    date_delta = (datetime.now() - date).total_seconds()
    suffix = ""
    if date_delta > 86400:
        date_delta = date_delta // 86400
        suffix = f"{date_delta} д. назад!"
    elif date_delta > 3600:
        date_delta = (date_delta % 86400) // 3600
        suffix = f"{date_delta} ч. назад!"
    elif date_delta > 60:
        date_delta = (date_delta % 3600) // 60
        suffix = f"{date_delta} мин. назад!"
    elif date_delta > 15:
        date_delta = date_delta % 60
        suffix = f"{date_delta} сек. назад!"
    else:
        suffix = f"было только что!"
    await message.answer(
        f"👤 <b>Это ты - {name}!</b>\n\n"
        f"Ты здесь с <code>{date.strftime('%d.%m.%Y %H:%M')}</code> (<i>это {suffix}</i>)\n"
        f"Записей - <b>{total_notes}</b> шт."
    )

@generic_router.message(F.text == "Помощь")
async def help_button(message: Message):
    await message.answer("Извини, пока что в разработке.")


@generic_router.message(F.text == "Назад")
async def back_button(message: Message):
    await message.answer("И мы вернулись.", reply_markup=main_keyboard())