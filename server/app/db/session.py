from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

# Convert postgresql:// to postgresql+asyncpg:// for async driver
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

if "?" in db_url:
    db_url = db_url.split("?")[0]

engine = create_async_engine(db_url, echo=True, connect_args={"ssl": "require"})
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
