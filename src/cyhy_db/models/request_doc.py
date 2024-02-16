# Standard Python Libraries
from datetime import datetime
from ipaddress import IPv4Network
import re
from typing import List, Optional

# Third-Party Libraries
from beanie import Document, Insert, Link, Replace, ValidateOnSave, before_event
from pydantic import BaseModel, EmailStr, Field, field_validator

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

from ..utils import utcnow

BOGUS_ID = "bogus_id_replace_me"


class Contact(BaseModel):
    email: EmailStr
    name: str
    phone: str
    type: PocType


class Location(BaseModel):
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
    name: str
    acronym: str
    type: Optional[AgencyType] = Field(default=None)
    contacts: List[Contact] = Field(default=[])
    location: Optional[Location] = Field(default=None)


class ScanLimit(BaseModel):
    scan_type: ScanType = Field(..., alias="scanType")
    concurrent: int = Field(ge=0)


class Window(BaseModel):
    day: DayOfWeek = Field(default=DayOfWeek.SUNDAY)
    duration: int = Field(default=168, ge=0, le=168)
    start: str = Field(default="00:00:00")

    @field_validator("start")
    def validate_start(cls, v):
        # Validate that the start time is in the format HH:MM:SS
        if not re.match(r"^\d{2}:\d{2}:\d{2}$", v):
            raise ValueError("Start time must be in the format HH:MM:SS")
        return v


class RequestDoc(Document):
    id: str = Field(default=BOGUS_ID)
    agency: Agency
    children: List[Link["RequestDoc"]] = Field(default=[])
    enrolled: datetime = Field(default_factory=utcnow)
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
        # Set the id to the agency acronym if it is the default value
        if self.id == BOGUS_ID:
            self.id = self.agency.acronym

    class Settings:
        # Beanie settings
        name = "requests"
        indexes = []
