"""The model for CyHy tally documents."""

# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from beanie import Document, Insert, Replace, ValidateOnSave, before_event
from pydantic import BaseModel, ConfigDict, Field

from ..utils import utcnow


class StatusCounts(BaseModel):
    """The model for host status counts."""

    model_config = ConfigDict(extra="forbid")

    DONE: int = 0
    READY: int = 0
    RUNNING: int = 0
    WAITING: int = 0


class Counts(BaseModel):
    """The model for scan stage counts."""

    model_config = ConfigDict(extra="forbid")

    BASESCAN: StatusCounts = Field(default_factory=StatusCounts)
    NETSCAN1: StatusCounts = Field(default_factory=StatusCounts)
    NETSCAN2: StatusCounts = Field(default_factory=StatusCounts)
    PORTSCAN: StatusCounts = Field(default_factory=StatusCounts)
    VULNSCAN: StatusCounts = Field(default_factory=StatusCounts)


class TallyDoc(Document):
    """The tally document model."""

    model_config = ConfigDict(extra="forbid")

    _id: str  # owner_id
    counts: Counts = Field(default_factory=Counts)
    last_change: datetime = Field(default_factory=utcnow)

    @before_event(Insert, Replace, ValidateOnSave)
    async def before_save(self):
        """Set data just prior to saving a tally document."""
        self.last_change = utcnow()

    class Settings:
        """Beanie settings."""

        name = "tallies"
