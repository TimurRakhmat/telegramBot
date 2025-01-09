from bot import logger
from base import connection
from models import User, Rating, Place
from sqlalchemy import select, func
from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError


@connection
async def set_user(session, tg_id: int, username: str, full_name: str) -> Optional[User]:
    try:
        user = await session.scalar(select(User).filter_by(id=tg_id))

        if not user:
            new_user = User(id=tg_id, username=username, full_name=full_name)
            session.add(new_user)
            await session.commit()
            logger.info(f"Зарегистрировал пользователя с ID {tg_id}!")
            return None
        else:
            logger.info(f"Пользователь с ID {tg_id} найден!")
            return user
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении пользователя: {e}")
        await session.rollback()


@connection
async def add_place(session, placename: str,
                   active_recreation: Optional[int] = 0,
                   cultural_event: Optional[int] = 0, 
                   nightlife: Optional[int] = 0, 
                   file_id: Optional[str] = None) -> Optional[Place]:
    try:
        new_place = Place(
            placename = placename,
            active_recreation = active_recreation,
            cultural_event = cultural_event,
            nightlife = nightlife,
            img_id = file_id
        )

        session.add(new_place)
        await session.commit()
        logger.info(f"Новое место с ID {new_place.id} успешно добавлена")
        return new_place
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении места: {e}")
        await session.rollback()


@connection
async def add_rate(session, user_id: int, place_id: int, rating: Optional[int] = 0) -> Optional[Rating]:
    try:
        user = await session.scalar(select(User).filter_by(id=user_id))
        place = await session.scalar(select(Place).filter_by(id=place_id))
        rate = await session.scalar(select(Rating).filter_by(place_id=place_id, user_id=user_id))
        if not user:
            logger.error(f"Пользователь с ID {user_id} не найден.")
            return None
        
        if not place:
            logger.error(f"Место с ID {place_id} не найдено.")
            return None
        new_rate = None
        if rate:
            rate.rating = rating
            new_rate = rate
        else:
            new_rate = Rating(
                user_id=user_id,
                place_id=place_id,
                rating=rating
            )
            session.add(new_rate)
        await session.commit()
        logger.info(f"Оценка пользователя с ID {user_id} успешно добавлена!")
        return new_rate
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении оценки: {e}")
        await session.rollback()


@connection
async def get_place(session,
                   offset: Optional[int] = 0,
                   user_id: Optional[int] = 0,
                   active_recreation: Optional[int] = 0,
                   cultural_event: Optional[int] = 0, 
                   nightlife: Optional[int] = 0) -> Optional[Place]:
    try:
        result = await session.execute( select(Place, func.avg(Rating.rating).label('average_rating'))\
        .join(Rating, Place.id == Rating.place_id, isouter=True)\
        .where(Rating.user_id != user_id)\
        .group_by(Place.id)\
        .order_by(func.avg(Rating.rating).desc())\
        .offset(offset - 1) \
        .limit(1))

        result = result.first()
        if not result:
            return
        place, average_rating = result
        return place
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при поиске места: {e}")


@connection
async def get_user_rating_matrix(session, user_id: int):
    users = await session.execute( select(User.id).order_by(User.id))
    users = [user[0] for user in users]
    
    places = await session.execute( select(Place.id).order_by(Place.id))
    places = [place[0] for place in places]
    
    rating_matrix = np.zeros((len(users), len(places)))
    
    ratings = await session.execute( select(Rating.user_id, Rating.place_id, Rating.rating))
    
    for user_id, place_id, rating in ratings:
        user_index = users.index(user_id)
        place_index = places.index(place_id)
        rating_matrix[user_index, place_index] = rating
    
    return users, places, rating_matrix


async def find_similar_users(user_id, top_n=5):
    users, places, rating_matrix = await get_user_rating_matrix(user_id)
    user_index = users.index(user_id)
    user_vector = rating_matrix[user_index].reshape(1, -1)
    
    similarities = cosine_similarity(user_vector, rating_matrix)[0]
    
    similar_users = [
        (users[i], similarity)
        for i, similarity in enumerate(similarities)
        if users[i] != user_id
    ]
    similar_users.sort(key=lambda x: x[1], reverse=True)
    
    return similar_users[:top_n]

@connection
async def get_best_place(session,
                   offset: Optional[int] = 0,
                   user_id: Optional[int] = 0,
                   active_recreation: Optional[int] = 0,
                   cultural_event: Optional[int] = 0, 
                   nightlife: Optional[int] = 0) -> Optional[Place]:
    try:
        bestUsers = await find_similar_users(user_id, 2)
        best_id = [bestUser[0] for bestUser in bestUsers]

        result = await session.execute( select(Place, func.avg(Rating.rating).label('average_rating'))\
        .join(Rating, Place.id == Rating.place_id, isouter=True)\
        .filter(not_(Place.id.in_(select(Rating.id).filter(Rating.user_id == user_id).subquery())))\
        .filter(Rating.user_id.in_(best_id))\
        .group_by(Place.id)\
        .order_by(func.avg(Rating.rating).desc())\
        .offset(offset - 1) \
        .limit(1))

        result = result.first()
        if not result:
            return
        place, average_rating = result
        return place
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при поиске места: {e}")