from typing import Dict
from pydantic import ConfigDict
from pymongo import ASCENDING, IndexModel
from datetime import datetime

from . import ScanDoc
from .enum import Protocol


class VulnScanDoc(ScanDoc):
    model_config = ConfigDict(extra="forbid")

    protocol: Protocol
    port: int
    service: str
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
    risk_factor: str
    severity: int
    solution: str
    synopsis: str

    class Settings:
        # Beanie settings
        name = "vuln_scans"
        indexes = [
            IndexModel(
                [("owner", ASCENDING), ("latest", ASCENDING), ("severity", ASCENDING)],
                name="owner_latest_severity",
            ),
        ]
