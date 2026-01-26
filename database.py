from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from models import Base

DATABASE_URL = "sqlite+aiosqlite:///./db.sqlite3"

# 1. Engine — сердце базы. Echo=True покажет в консоли все SQL-запросы (полезно для обучения)
engine = create_async_engine(DATABASE_URL, echo=True)

# 2. Sessionmaker — фабрика для создания сессий (подключений)
async_session = async_sessionmaker(engine, expire_on_commit=False)

# Функция для создания таблиц (вызовем её при старте бота)
async def init_db():
    async with engine.begin() as conn:
       # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)