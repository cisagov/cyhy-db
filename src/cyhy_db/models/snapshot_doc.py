"""The model for CyHy snapshot documents."""

# Standard Python Libraries
from datetime import datetime
from ipaddress import IPv4Network
from typing import Dict, List

# Third-Party Libraries
from beanie import Document
from pydantic import BaseModel, ConfigDict, Field
from pymongo import ASCENDING, IndexModel

from ..utils import utcnow


class VulnerabilityCounts(BaseModel):
    """The model for vulnerability counts."""

    model_config = ConfigDict(extra="forbid")

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    total: int = 0


class WorldData(BaseModel):
    """The model for aggregated metrics of all CyHy entities."""

    model_config = ConfigDict(extra="forbid")

    cvss_average_all: float = 0.0
    cvss_average_vulnerable: float = 0.0
    host_count: int = 0
    unique_vulnerabilities: VulnerabilityCounts = Field(
        default_factory=VulnerabilityCounts
    )
    vulnerable_host_count: int = 0
    vulnerabilities: VulnerabilityCounts = Field(default_factory=VulnerabilityCounts)


class TicketMetrics(BaseModel):
    """The model for ticket metrics."""

    model_config = ConfigDict(extra="forbid")

    max: int = 0
    median: int = 0


class TicketOpenMetrics(BaseModel):
    """The model for open ticket metrics."""

    model_config = ConfigDict(extra="forbid")

    # Numbers in this section refer to how long open tix were open AT this date/time
    tix_open_as_of_date: datetime = Field(default_factory=utcnow)
    critical: TicketMetrics = Field(default_factory=TicketMetrics)
    high: TicketMetrics = Field(default_factory=TicketMetrics)
    medium: TicketMetrics = Field(default_factory=TicketMetrics)
    low: TicketMetrics = Field(default_factory=TicketMetrics)


class TicketCloseMetrics(BaseModel):
    """The model for closed ticket metrics."""

    model_config = ConfigDict(extra="forbid")

    # Numbers in this section only include tix that closed AT/AFTER this date/time
    tix_closed_after_date: datetime = Field(default_factory=utcnow)
    critical: TicketMetrics = Field(default_factory=TicketMetrics)
    high: TicketMetrics = Field(default_factory=TicketMetrics)
    medium: TicketMetrics = Field(default_factory=TicketMetrics)
    low: TicketMetrics = Field(default_factory=TicketMetrics)


class SnapshotDoc(Document):
    """The snapshot document model."""

    model_config = ConfigDict(extra="forbid")

    addresses_scanned: int = Field(default=0)
    cvss_average_all: float = Field(default=0.0)
    cvss_average_vulnerable: float = Field(default=0.0)
    descendants_included: List[str] = Field(default=[])
    end_time: datetime = Field(...)
    host_count: int = Field(default=0)
    last_change: datetime = Field(default_factory=utcnow)
    latest: bool = Field(default=True)
    networks: List[IPv4Network] = Field(default=[])
    owner: str = Field(...)
    port_count: int = Field(default=0)
    services: Dict = Field(default_factory=dict)
    start_time: datetime = Field(...)
    tix_msec_open: TicketOpenMetrics = Field(default_factory=TicketOpenMetrics)
    tix_msec_to_close: TicketCloseMetrics = Field(default_factory=TicketCloseMetrics)
    unique_operating_systems: int = Field(default=0)
    unique_port_count: int = Field(default=0)
    unique_vulnerabilities: VulnerabilityCounts = Field(
        default_factory=VulnerabilityCounts
    )
    vulnerabilities: VulnerabilityCounts = Field(default_factory=VulnerabilityCounts)
    vulnerable_host_count: int = Field(default=0)
    world: WorldData = Field(default_factory=WorldData)

    class Settings:
        """Beanie settings."""

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
