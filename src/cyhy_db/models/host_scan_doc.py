"""The model for CyHy host scan documents."""

# Standard Python Libraries
from typing import List

# Third-Party Libraries
from pydantic import ConfigDict
from pymongo import ASCENDING, IndexModel

from . import ScanDoc


class HostScanDoc(ScanDoc):
    """The host scan document model."""

    model_config = ConfigDict(extra="forbid")

    accuracy: int
    classes: List[dict] = []
    line: int
    name: str

    class Settings:
        """Beanie settings."""

        name = "host_scans"
        indexes = ScanDoc.Abstract_Settings.indexes + [
            IndexModel(
                [("latest", ASCENDING), ("owner", ASCENDING)], name="latest_owner"
            ),
            IndexModel([("owner", ASCENDING)], name="owner"),
        ]
