from beanie import Document, before_event, Insert, Replace, ValidateOnSave
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from ..utils import utcnow


class StatusCounts(BaseModel):
    model_config = ConfigDict(extra="forbid")

    DONE: int = 0
    READY: int = 0
    RUNNING: int = 0
    WAITING: int = 0


class Counts(BaseModel):
    model_config = ConfigDict(extra="forbid")

    BASESCAN: StatusCounts = Field(default_factory=StatusCounts)
    NETSCAN1: StatusCounts = Field(default_factory=StatusCounts)
    NETSCAN2: StatusCounts = Field(default_factory=StatusCounts)
    PORTSCAN: StatusCounts = Field(default_factory=StatusCounts)
    VULNSCAN: StatusCounts = Field(default_factory=StatusCounts)


class TallyDoc(Document):
    model_config = ConfigDict(extra="forbid")

    _id: str  # owner_id
    counts: Counts = Field(default_factory=Counts)
    last_change: datetime = Field(default_factory=utcnow)

    @before_event(Insert, Replace, ValidateOnSave)
    async def before_save(self):
        self.last_change = utcnow()

    class Settings:
        name = "tallies"
