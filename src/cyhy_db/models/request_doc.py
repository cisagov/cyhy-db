"""The model for CyHy request documents."""

# Standard Python Libraries
from datetime import datetime, time
from ipaddress import IPv4Network
from typing import List, Optional

# Third-Party Libraries
from beanie import Document, Insert, Link, Replace, ValidateOnSave, before_event
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from ..utils import utcnow
from .enum import (
    AgencyType,
    DayOfWeek,
    PocType,
    ReportPeriod,
    ReportType,
    ScanType,
    Scheduler,
    Stage,
)

BOGUS_ID = "bogus_id_replace_me"


class Contact(BaseModel):
    """A point of contact for the entity."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    name: str
    phone: str
    type: PocType


class Location(BaseModel):
    """A location with various geographical identifiers."""

    model_config = ConfigDict(extra="forbid")

    country_name: str
    country: str
    county_fips: str
    county: str
    gnis_id: int
    name: str
    state_fips: str
    state_name: str
    state: str


class Agency(BaseModel):
    """Model representing a CyHy-enrolled entity."""

    model_config = ConfigDict(extra="forbid")

    name: str
    acronym: str
    type: Optional[AgencyType] = Field(default=None)
    contacts: List[Contact] = Field(default=[])
    location: Optional[Location] = Field(default=None)


class ScanLimit(BaseModel):
    """Scan limits for a specific scan type."""

    model_config = ConfigDict(extra="forbid")

    scan_type: ScanType = Field(..., alias="scanType")
    concurrent: int = Field(ge=0)


class Window(BaseModel):
    """A day and time window for scheduling scans."""

    model_config = ConfigDict(extra="forbid")

    day: DayOfWeek = Field(default=DayOfWeek.SUNDAY)
    duration: int = Field(default=168, ge=0, le=168)
    start: time = Field(default=time(0, 0, 0))

    @field_validator("start", mode="before")
    @classmethod
    def parse_time(cls, v):
        """Parse and validate a time representation."""
        if isinstance(v, str):
            # Parse the string to datetime.time
            return datetime.strptime(v, "%H:%M:%S").time()
        elif isinstance(v, time):
            return v
        else:
            raise ValueError(
                "Invalid time format. Expected a string in '%H:%M:%S' format or datetime.time instance."
            )


class RequestDoc(Document):
    """The request document model."""

    model_config = ConfigDict(extra="forbid")

    agency: Agency
    children: List[Link["RequestDoc"]] = Field(default=[])
    enrolled: datetime = Field(default_factory=utcnow)
    id: str = Field(default=BOGUS_ID)  # type: ignore[assignment]
    init_stage: Stage = Field(default=Stage.NETSCAN1)
    key: Optional[str] = Field(default=None)
    networks: List[IPv4Network] = Field(default=[])
    period_start: datetime = Field(default_factory=utcnow)
    report_period: ReportPeriod = Field(default=ReportPeriod.WEEKLY)
    report_types: List[ReportType] = Field(default=[])
    retired: bool = False
    scan_limits: List[ScanLimit] = Field(default=[])
    scan_types: List[ScanType] = Field(default=[])
    scheduler: Scheduler = Field(default=Scheduler.PERSISTENT1)
    stakeholder: bool = False
    windows: List[Window] = Field(default=[Window()])

    @before_event(Insert, Replace, ValidateOnSave)
    async def set_id_to_acronym(self):
        """Set the id to the agency acronym if it is the default value."""
        if self.id == BOGUS_ID:
            self.id = self.agency.acronym

    class Settings:
        """Beanie settings."""

        bson_encoders = {
            time: lambda value: value.strftime("%H:%M:%S")
        }  # Register custom encoder for datetime.time
        name = "requests"
