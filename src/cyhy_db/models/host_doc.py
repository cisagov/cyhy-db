from beanie import Document, before_event, Indexed, Insert, Replace, ValidateOnSave
from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from pymongo import ASCENDING, IndexModel
from typing import Any, Dict, Optional, Tuple
import random
from .enum import Stage, Status
from ipaddress import IPv4Address, ip_address


class State(BaseModel):
    reason: str
    up: bool


class HostDoc(Document):
    id: int = Field(...)  # IP address as an integer
    ip: IPv4Address = Field(...)
    owner: str = Field(...)
    last_change: datetime = Field(default_factory=datetime.utcnow)
    next_scan: Optional[datetime] = Field(default=None)
    state: State = Field(default_factory=lambda: State(reason="new", up=False))
    stage: Stage = Field(default=Stage.NETSCAN1)
    status: Status = Field(default=Status.WAITING)
    loc: Optional[Tuple[float, float]] = Field(default=None)
    priority: int = Field(default=0)
    r: float = Field(default_factory=random.random)
    latest_scan: Dict[Stage, datetime] = Field(default_factory=dict)

    @model_validator(mode="before")
    def calculate_ip_int(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # ip may still be string if it was just set
        values["id"] = int(ip_address(values["ip"]))
        print(values)
        return values

    @before_event(Insert, Replace, ValidateOnSave)
    async def before_save(self):
        self.last_change = datetime.utcnow()

    class Settings:
        name = "hosts"
        indexes = [
            IndexModel(
                [
                    ("status", ASCENDING),
                    ("stage", ASCENDING),
                    ("owner", ASCENDING),
                    ("priority", ASCENDING),
                    ("r", ASCENDING),
                ],
                name="claim",
            ),
            IndexModel(
                [
                    ("ip", ASCENDING),
                ],
                name="ip",
            ),
            IndexModel(
                [
                    ("state.up", ASCENDING),
                    ("owner", ASCENDING),
                ],
                name="up",
            ),
            IndexModel(
                [
                    ("next_scan", ASCENDING),
                    ("state.up", ASCENDING),
                    ("status", ASCENDING),
                ],
                sparse=True,
                name="next_scan",
            ),
            IndexModel(
                [
                    ("owner", ASCENDING),
                ],
                name="owner",
            ),
            IndexModel(
                [
                    ("owner", ASCENDING),
                    ("state.up", ASCENDING),
                    ("latest_scan.VULNSCAN", ASCENDING),
                ],
                name="latest_scan_done",
            ),
        ]
