# Third-Party Libraries
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from .models.cve import CVE
from .models.request_doc import RequestDoc
from .models.scan_doc import ScanDoc
from .models.snapshot_doc import SnapshotDoc

ALL_MODELS = [CVE, RequestDoc, ScanDoc, SnapshotDoc]


async def initialize_db(db_uri: str, db_name: str) -> None:
    try:
        client = AsyncIOMotorClient(db_uri)
        db = client[db_name]
        await init_beanie(database=db, document_models=ALL_MODELS)
        return db
    except Exception as e:
        print(f"Failed to initialize database with error: {e}")
        raise
