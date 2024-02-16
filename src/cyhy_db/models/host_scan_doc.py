from . import ScanDoc
from typing import List
from pymongo import ASCENDING, IndexModel


class HostScanDoc(ScanDoc):
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
