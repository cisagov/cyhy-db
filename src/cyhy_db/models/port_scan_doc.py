from typing import Dict
from pymongo import ASCENDING, IndexModel
from pydantic import ConfigDict

from . import ScanDoc
from .enum import Protocol


class PortScanDoc(ScanDoc):
    model_config = ConfigDict(extra="forbid")
    protocol: Protocol
    port: int
    service: Dict = {}  # Assuming no specific structure for "service"
    state: str
    reason: str

    class Settings:
        # Beanie settings
        name = "port_scans"
        indexes = [
            IndexModel(
                [("latest", ASCENDING), ("owner", ASCENDING), ("state", ASCENDING)],
                name="latest_owner_state",
            ),
            IndexModel(
                [("latest", ASCENDING), ("service.name", ASCENDING)],
                name="latest_service_name",
            ),
            IndexModel(
                [("latest", ASCENDING), ("time", ASCENDING)],
                name="latest_time",
            ),
            IndexModel(
                [("owner", ASCENDING)],
                name="owner",
            ),
        ]
