from . import ScanDoc
from typing import List
from pymongo import ASCENDING, IndexModel
from pydantic import ConfigDict


class HostScanDoc(ScanDoc):
    model_config = ConfigDict(extra="forbid")

    name: str
    accuracy: int
    line: int
    classes: List[dict] = []

    class Settings:
        # Beanie settings
        name = "host_scans"
        indexes = [
            IndexModel(
                [("latest", ASCENDING), ("owner", ASCENDING)], name="latest_owner"
            ),
            IndexModel([("owner", ASCENDING)], name="owner"),
        ]
