import asyncio
from app.db.session import AsyncSessionLocal
from app.models.procurement_request import ProcurementRequest as DBProcurementRequest
from app.schemas.procurement_request import ProcurementRequest
from sqlalchemy.future import select
import uuid

async def main():
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(DBProcurementRequest))
            requests = result.scalars().all()
            for r in requests:
                try:
                    p = ProcurementRequest.model_validate(r)
                    print(f"Validated {p.id}")
                except Exception as ve:
                    print(f"Validation Error for {r.id}: {ve}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
