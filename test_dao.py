import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base, User, Place, Rating
from dao import set_user, add_place, add_rate, get_place, find_similar_users

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Создание движка и сессии
@pytest.fixture
async def async_session():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Создаем таблицы

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_set_user(async_session):
    user = await set_user(async_session, tg_id=1, username="testuser", full_name="Test User")
    assert user is None  # Первый вызов создает пользователя
    user = await set_user(async_session, tg_id=1, username="testuser", full_name="Test User")
    assert user is not None  # Второй вызов возвращает пользователя


@pytest.mark.asyncio
async def test_add_place(async_session):
    place = await add_place(async_session, placename="Test Place", active_recreation=5, cultural_event=7, nightlife=6)
    assert place is not None
    assert place.placename == "Test Place"


@pytest.mark.asyncio
async def test_add_rate(async_session):
    # Добавление пользователя и места
    user = await set_user(async_session, tg_id=1, username="testuser", full_name="Test User")
    place = await add_place(async_session, placename="Test Place", active_recreation=5, cultural_event=7, nightlife=6)
    
    # Добавление оценки
    rate = await add_rate(async_session, user_id=1, place_id=1, rating=8)
    assert rate is not None
    assert rate.rating == 8

    # Обновление оценки
    rate = await add_rate(async_session, user_id=1, place_id=1, rating=9)
    assert rate.rating == 9


@pytest.mark.asyncio
async def test_get_place(async_session):
    # Добавляем пользователя, место и рейтинг
    user = await set_user(async_session, tg_id=1, username="testuser", full_name="Test User")
    place = await add_place(async_session, placename="Test Place", active_recreation=5, cultural_event=7, nightlife=6)

    await add_rate(async_session, user_id=1, place_id=1, rating=9)

    # Получение места
    place = await get_place(async_session, user_id=2, offset=1)
    assert place is not None
    assert place.placename == "Test Place"


@pytest.mark.asyncio
async def test_find_similar_users(async_session):
    # Добавляем пользователей и их оценки
    user1 = await set_user(async_session, tg_id=1, username="testuser1", full_name="Test User")
    user2 = await set_user(async_session, tg_id=1, username="testuser2", full_name="Test User")
    place = await add_place(async_session, placename="Test Place", active_recreation=5, cultural_event=7, nightlife=6)

    await add_rate(async_session, user_id=1, place_id=1, rating=9)
    await add_rate(async_session, user_id=2, place_id=1, rating=9)

    # Проверяем сходство
    similar_users = await find_similar_users(1, top_n=1)
    assert len(similar_users) == 1
    assert similar_users[0][0] == 2  # ID похожего пользователя
