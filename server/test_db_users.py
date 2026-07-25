import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def main():
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(text("SELECT id, clerk_id, email, name FROM users"))
            users = result.fetchall()
            print("Users in DB:")
            for u in users:
                print(u)
        except Exception as e:
            print(f"Error querying users: {e}")

if __name__ == "__main__":
    asyncio.run(main())
