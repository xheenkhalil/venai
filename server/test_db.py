import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def main():
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(text("SELECT count(*) FROM users"))
            count = result.scalar()
            print(f"Users table exists. Row count: {count}")
        except Exception as e:
            print(f"Error querying users: {e}")

if __name__ == "__main__":
    asyncio.run(main())
