from DataBase.database import async_session_maker


async def get_bd():
    async with async_session_maker() as session:
        yield session
