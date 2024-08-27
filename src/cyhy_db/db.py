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
    ScanDoc,
    SnapshotDoc,
    SystemControlDoc,
    TallyDoc,
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
    ScanDoc,
    SnapshotDoc,
    SystemControlDoc,
    TallyDoc,
    VulnScanDoc,
]


async def initialize_db(db_uri: str, db_name: str) -> AsyncIOMotorDatabase:
    try:
        client: AsyncIOMotorClient = AsyncIOMotorClient(db_uri)
        db: AsyncIOMotorDatabase = client[db_name]
        await init_beanie(database=db, document_models=ALL_MODELS)
        return db
    except Exception as e:
        print(f"Failed to initialize database with error: {e}")
        raise
