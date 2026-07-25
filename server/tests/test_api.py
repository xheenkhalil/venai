import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.dependencies import get_current_user
from app.api.v1.endpoints.procurement_requests import get_db as get_db_pr
from app.api.v1.endpoints.vendors import get_db as get_db_v
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

def mock_get_current_user():
    return {
        "sub": "test_clerk_id_123",
        "email": "test_pytest@example.com",
        "name": "Test User"
    }

async def mock_get_db():
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if "?" in db_url:
        db_url = db_url.split("?")[0]
    
    # Create engine inside the current event loop
    engine = create_async_engine(db_url, echo=False, connect_args={"ssl": "require"})
    TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
    
    async with TestingSessionLocal() as session:
        yield session
    
    await engine.dispose()

app.dependency_overrides[get_current_user] = mock_get_current_user
app.dependency_overrides[get_db_pr] = mock_get_db
app.dependency_overrides[get_db_v] = mock_get_db

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

@pytest.mark.asyncio
async def test_get_procurement_requests(async_client):
    response = await async_client.get("/api/v1/procurement-requests/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_create_procurement_request(async_client):
    payload = {
        "title": "Test Request",
        "product_name": "Test Product",
        "quantity": 100,
        "budget": "5000",
        "currency": "USD"
    }
    response = await async_client.post("/api/v1/procurement-requests/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Request"
    assert "id" in data

@pytest.mark.asyncio
async def test_get_vendors(async_client):
    response = await async_client.get("/api/v1/vendors/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
