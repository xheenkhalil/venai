import asyncio
from app.db.session import AsyncSessionLocal
from app.models.procurement_request import ProcurementRequest as DBProcurementRequest
from sqlalchemy.future import select
import uuid

async def main():
    async with AsyncSessionLocal() as session:
        try:
            org_id = uuid.uuid4()
            result = await session.execute(
                select(DBProcurementRequest)
                .filter(DBProcurementRequest.organization_id == org_id)
                .order_by(DBProcurementRequest.created_at.desc())
            )
            print("Query executed successfully.")
            requests = result.scalars().all()
            print(requests)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
