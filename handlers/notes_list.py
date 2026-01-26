from datetime import datetime

from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from keyboards import main_keyboard
from states import Survey
from database import async_session
from sqlalchemy import select, func, desc
from models import User, Rates

router = Router()

@router.message(F.text == "📔 Записи")
async def note_list(message: Message, state: FSMContext) -> None:
    bot_message = await message.answer("Получаю список записей...")
    page = 1
    notes_text = []
    async with async_session() as session:
        user_filter = Rates.tg_id == message.from_user.id

        # скока всего записей
        count_query = select(func.count()).select_from(Rates).where(user_filter)
        total = (await session.execute(count_query)).scalar()

        # все записи
        notes_query = (
            select(Rates)
            .where(user_filter)
            .order_by(Rates.rate_date)
            .offset((page - 1) * 5)
            .limit(5)
        )
        notes = (await session.execute(notes_query)).scalars().all()

        total_pages = (total + 4) // 5
    for note in notes:
        rate = note.rate
        comment = note.note
        created_at = note.created_at
        rate_date = note.rate_date
        notes_text.append(f"Запись от {rate_date}\n"
                          f"Запись создана {created_at}\n"
                          f"Оценка дня: <b>{rate}</b>\n"
                          f"Комментарий дня:\n"
                          f"<blockquote>{comment}</blockquote>")
    await bot_message.edit_text(text="\n\n".join(notes_text))