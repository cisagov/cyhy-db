from beanie import Document, before_event, Insert, Replace, ValidateOnSave
from datetime import datetime
from pydantic import BaseModel, Field

from ..utils import utcnow


class StatusCounts(BaseModel):
    READY: int = 0
    WAITING: int = 0
    DONE: int = 0
    RUNNING: int = 0


class Counts(BaseModel):
    PORTSCAN: StatusCounts = Field(default_factory=StatusCounts)
    BASESCAN: StatusCounts = Field(default_factory=StatusCounts)
    VULNSCAN: StatusCounts = Field(default_factory=StatusCounts)
    NETSCAN1: StatusCounts = Field(default_factory=StatusCounts)
    NETSCAN2: StatusCounts = Field(default_factory=StatusCounts)


class TallyDoc(Document):
    _id: str  # owner_id
    counts: Counts = Field(default_factory=Counts)
    last_change: datetime = Field(default_factory=utcnow)

    @before_event(Insert, Replace, ValidateOnSave)
    async def before_save(self):
        self.last_change = utcnow()

    class Settings:
        name = "tallies"
