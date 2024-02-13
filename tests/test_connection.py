"""Test database connection."""

# Third-Party Libraries
from motor.motor_asyncio import AsyncIOMotorClient

# cisagov Libraries
from cyhy_db import initialize_db
from cyhy_db.models import CVE


async def test_connection_motor(db_uri, db_name):
    client = AsyncIOMotorClient(db_uri)
    db = client[db_name]
    server_info = await db.command("ping")
    assert server_info["ok"] == 1.0, "Direct database ping failed"


async def test_connection_beanie():
    # Attempt to find a document in the empty CVE collection
    # await initialize_db(db_uri, db_name)  # Manually initialize for testing
    result = await CVE.get("CVE-2024-DOES-NOT-EXIST")
    assert result is None, "Expected no document to be found"
