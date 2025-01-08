from sqlalchemy import BigInteger, Integer, Text, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database import Base


class Rating(Base):
    __tablename__ = 'ratings'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    place_id: Mapped[int] = mapped_column(Integer, ForeignKey('places.id'), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=True, default=0)

    __table_args__ = (
        UniqueConstraint('user_id', 'place_id', name='unique_user_place'),
    )

    user = relationship("User", back_populates="ratings")
    place = relationship("Place", back_populates="ratings")


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    full_name: Mapped[str] = mapped_column(String, nullable=True)

    ratings = relationship("Rating", back_populates="user")


class Place(Base):
    __tablename__ = 'places'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    placename: Mapped[str] = mapped_column(String, nullable=False)
    active_recreation: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    cultural_event: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    nightlife: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    img_id: Mapped[str] = mapped_column(String, nullable=True)

    ratings = relationship("Rating", back_populates="place")