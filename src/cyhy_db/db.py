# Third-Party Libraries
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from .models import *


ALL_MODELS = [
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


async def initialize_db(db_uri: str, db_name: str) -> None:
    try:
        client = AsyncIOMotorClient(db_uri)
        db = client[db_name]
        await init_beanie(database=db, document_models=ALL_MODELS)
        return db
    except Exception as e:
        print(f"Failed to initialize database with error: {e}")
        raise
