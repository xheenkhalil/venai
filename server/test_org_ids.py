import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def main():
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(text("SELECT id, organization_id, title FROM procurement_requests"))
            rows = result.fetchall()
            print("Procurement Requests:")
            for r in rows:
                print(r)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
