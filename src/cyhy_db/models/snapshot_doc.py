# Standard Python Libraries
from datetime import datetime
from ipaddress import IPv4Network

# Third-Party Libraries
from beanie import Document
from pydantic import Field, ConfigDict
from pymongo import ASCENDING, IndexModel
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict
from bson import ObjectId

from ..utils import utcnow


class VulnerabilityCounts(BaseModel):
    model_config = ConfigDict(extra="forbid")

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    total: int = 0


class WorldData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    host_count: int = 0
    vulnerable_host_count: int = 0
    vulnerabilities: VulnerabilityCounts = Field(default_factory=VulnerabilityCounts)
    unique_vulnerabilities: VulnerabilityCounts = Field(
        default_factory=VulnerabilityCounts
    )
    cvss_average_all: float = 0.0
    cvss_average_vulnerable: float = 0.0


class TicketMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    median: int = 0
    max: int = 0


class TicketOpenMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Numbers in this section refer to how long open tix were open AT this date/time
    tix_open_as_of_date: datetime = Field(default_factory=utcnow)
    critical: TicketMetrics = Field(default_factory=TicketMetrics)
    high: TicketMetrics = Field(default_factory=TicketMetrics)
    medium: TicketMetrics = Field(default_factory=TicketMetrics)
    low: TicketMetrics = Field(default_factory=TicketMetrics)


class TicketCloseMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Numbers in this section only include tix that closed AT/AFTER this date/time
    tix_closed_after_date: datetime = Field(default_factory=utcnow)
    critical: TicketMetrics = Field(default_factory=TicketMetrics)
    high: TicketMetrics = Field(default_factory=TicketMetrics)
    medium: TicketMetrics = Field(default_factory=TicketMetrics)
    low: TicketMetrics = Field(default_factory=TicketMetrics)


class SnapshotDoc(Document):
    model_config = ConfigDict(extra="forbid")

    owner: str = Field(...)
    descendants_included: List[str] = Field(default=[])
    last_change: datetime = Field(default_factory=utcnow)
    start_time: datetime = Field(...)
    end_time: datetime = Field(...)
    latest: bool = Field(default=True)
    port_count: int = Field(default=0)
    unique_port_count: int = Field(default=0)
    unique_operating_systems: int = Field(default=0)
    host_count: int = Field(default=0)
    vulnerable_host_count: int = Field(default=0)
    vulnerabilities: VulnerabilityCounts = Field(default_factory=VulnerabilityCounts)
    unique_vulnerabilities: VulnerabilityCounts = Field(
        default_factory=VulnerabilityCounts
    )
    cvss_average_all: float = Field(default=0.0)
    cvss_average_vulnerable: float = Field(default=0.0)
    world: WorldData = Field(default_factory=WorldData)
    networks: List[IPv4Network] = Field(default=[])
    addresses_scanned: int = Field(default=0)
    services: Dict = Field(default_factory=dict)
    tix_msec_open: TicketOpenMetrics = Field(default_factory=TicketOpenMetrics)
    tix_msec_to_close: TicketCloseMetrics = Field(default_factory=TicketCloseMetrics)

    class Settings:
        # Beanie settings
        name = "snapshots"
        indexes = [
            IndexModel(
                [
                    ("owner", ASCENDING),
                    ("start_time", ASCENDING),
                    ("end_time", ASCENDING),
                ],
                name="uniques",
                unique=True,
            ),
            IndexModel(
                [("latest", ASCENDING), ("owner", ASCENDING)], name="latest_owner"
            ),
        ]
