from sqlalchemy import insert, select

from src.database import async_session
from src.database.models import User


class UserService:

    @staticmethod
    async def create_user(email) -> User:
        create_user_req = insert(User).values(email=email).returning(User)
        async with async_session() as session, session.begin():
            created_user_chunked = await session.execute(create_user_req)
            return created_user_chunked.scalar()

    @staticmethod
    async def get_user_by_id(id: int) -> User:
        async with async_session() as session:
            req = select(User).where(User.id == id)
            user_chunked = await session.execute(req)
            return user_chunked.scalar()
