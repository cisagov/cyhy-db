"""The model for CyHy port scan documents."""

# Third-Party Libraries
from pydantic import ConfigDict
from pymongo import ASCENDING, IndexModel

from . import ScanDoc
from .enum import Protocol


class PortScanDoc(ScanDoc):
    """The port scan document model."""

    model_config = ConfigDict(extra="forbid")

    port: int
    protocol: Protocol
    reason: str
    service: dict = {}  # Assuming no specific structure for "service"
    state: str

    class Settings:
        """Beanie settings."""

        name = "port_scans"
        indexes = ScanDoc.AbstractSettings.indexes + [
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
