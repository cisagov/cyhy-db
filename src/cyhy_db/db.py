"""CyHy database top-level functions."""

# Third-Party Libraries
from beanie import Document, View, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .models import (
    CVE,
    HostDoc,
    HostScanDoc,
    KEVDoc,
    NotificationDoc,
    PlaceDoc,
    PortScanDoc,
    ReportDoc,
    RequestDoc,
    SnapshotDoc,
    SystemControlDoc,
    TallyDoc,
    TicketDoc,
    VulnScanDoc,
)

ALL_MODELS: list[type[Document] | type[View] | str] = [
    CVE,
    HostDoc,
    HostScanDoc,
    KEVDoc,
    NotificationDoc,
    PlaceDoc,
    PortScanDoc,
    RequestDoc,
    ReportDoc,
    SnapshotDoc,
    SystemControlDoc,
    TallyDoc,
    TicketDoc,
    VulnScanDoc,
]

# Note: ScanDoc is intentionally excluded from the list of models to be imported
# or initialized because it is an abstract base class.


async def initialize_db(db_uri: str, db_name: str) -> AsyncIOMotorDatabase:
    """Initialize the database."""
    try:
        client: AsyncIOMotorClient = AsyncIOMotorClient(db_uri)
        db: AsyncIOMotorDatabase = client[db_name]
        await init_beanie(database=db, document_models=ALL_MODELS)
        return db
    except Exception as e:
        print(f"Failed to initialize database with error: {e}")
        raise
