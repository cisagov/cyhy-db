"""The model for CyHy vulnerability scan documents."""

# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from pydantic import ConfigDict
from pymongo import ASCENDING, IndexModel

from . import ScanDoc
from .enum import Protocol


class VulnScanDoc(ScanDoc):
    """The vulnerability scan document model."""

    model_config = ConfigDict(extra="forbid")

    cvss_base_score: float
    cvss_vector: str
    description: str
    fname: str
    plugin_family: str
    plugin_id: int
    plugin_modification_date: datetime
    plugin_name: str
    plugin_publication_date: datetime
    plugin_type: str
    port: int
    protocol: Protocol
    risk_factor: str
    service: str
    severity: int
    solution: str
    synopsis: str

    class Settings:
        """Beanie settings."""

        name = "vuln_scans"
        indexes = ScanDoc.Abstract_Settings.indexes + [
            IndexModel(
                [("owner", ASCENDING), ("latest", ASCENDING), ("severity", ASCENDING)],
                name="owner_latest_severity",
            ),
        ]
