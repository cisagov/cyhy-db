"""Test database connection."""

# Standard Python Libraries
from unittest.mock import AsyncMock, patch

# Third-Party Libraries
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pytest

# cisagov Libraries
from cyhy_db.db import ALL_MODELS, initialize_db
from cyhy_db.models import CVEDoc


async def test_connection_motor(db_uri, db_name):
    """Test connectivity to database."""
    client = AsyncIOMotorClient(db_uri)
    db = client[db_name]
    server_info = await db.command("ping")
    assert server_info["ok"] == 1.0, "Direct database ping failed"


async def test_connection_beanie():
    """Test a simple database query."""
    # Attempt to find a document in the empty CVE collection
    result = await CVEDoc.get("CVE-2024-DOES-NOT-EXIST")
    assert result is None, "Expected no document to be found"


# Confused about the order of patch statements relative to the order of the test
# function parameters?  See here:
# https://docs.python.org/3/library/unittest.mock.html#patch
@patch("cyhy_db.db.init_beanie", return_value=None)  # mock_init_beanie
@patch("cyhy_db.db.AsyncIOMotorClient")  # mock_async_iomotor_client
@pytest.mark.asyncio
async def test_initialize_db_success(mock_async_iomotor_client, mock_init_beanie):
    """Test a success case of the initialize_db function."""
    db_uri = "mongodb://localhost:27017"
    db_name = "test_db"

    mock_client = AsyncMock()
    mock_db = AsyncMock(AsyncIOMotorDatabase)
    mock_client.__getitem__.return_value = mock_db
    mock_async_iomotor_client.return_value = mock_client

    db = await initialize_db(db_uri, db_name)
    assert db == mock_db
    mock_async_iomotor_client.assert_called_once_with(db_uri)
    mock_init_beanie.assert_called_once_with(
        database=mock_db, document_models=ALL_MODELS
    )


@pytest.mark.asyncio
async def test_initialize_db_failure():
    """Test a failure case of the initialize_db function."""
    db_uri = "mongodb://localhost:27017"
    db_name = "test_db"

    with patch(
        "cyhy_db.db.AsyncIOMotorClient", side_effect=Exception("Connection error")
    ):
        with pytest.raises(Exception, match="Connection error"):
            await initialize_db(db_uri, db_name)
