from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime, date


# Базовый класс, от которого наследуются все таблицы
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"  # Имя таблицы в базе данных

    # Уникальный внутренний ID (автоматически растет)
    id: Mapped[int] = mapped_column(primary_key=True)

    # ID из Телеграма. Используем BigInteger, так как ID бывают очень длинными
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)

    # Имя человека
    name: Mapped[str] = mapped_column(String, nullable=False)

    # Выбранная шкала (например, 5, 10 или 100)
    # По умолчанию поставим None, пока юзер не выбрал её при старте
    scale: Mapped[int] = mapped_column(Integer, nullable=True)

    # Дата регистрации (заполнится сама при создании записи)
    registration_date: Mapped[datetime] = mapped_column(default=datetime.now)

class Rates(Base):

    __tablename__ = "rates"

    id: Mapped[int] = mapped_column(primary_key=True)

    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    rate: Mapped[int] = mapped_column(Integer, nullable=False)

    note: Mapped[str] = mapped_column(String, nullable=True)

    rate_date: Mapped[date] = mapped_column(default=date.today())

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)