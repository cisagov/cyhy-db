from beanie import Document, before_event, Indexed, Insert, Replace, ValidateOnSave
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, ConfigDict
from pymongo import ASCENDING, IndexModel
from typing import Any, Dict, Optional, Tuple
import random
from .enum import Stage, Status
from ipaddress import IPv4Address, ip_address
from ..utils import deprecated, utcnow


class State(BaseModel):
    reason: str
    up: bool


class HostDoc(Document):
    model_config = ConfigDict(extra="forbid")

    id: int = Field()  # IP address as an integer
    ip: IPv4Address = Field(...)
    owner: str = Field(...)
    last_change: datetime = Field(default_factory=utcnow)
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
        values["_id"] = int(ip_address(values["ip"]))
        return values

    @before_event(Insert, Replace, ValidateOnSave)
    async def before_save(self):
        self.last_change = utcnow()

    class Settings:
        # Beanie settings
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

    def set_state(self, nmap_says_up, has_open_ports, reason=None):
        """Sets state.up based on different stage
        evidence. nmap has a concept of up which is
        different from our definition. An nmap "up" just
        means it got a reply, not that there are any open
        ports. Note either argument can be None."""

        if has_open_ports == True:  # Only PORTSCAN sends in has_open_ports
            self.state = State(True, "open-port")
        elif has_open_ports == False:
            self.state = State(False, "no-open")
        elif nmap_says_up == False:  # NETSCAN says host is down
            self.state = State(False, reason)

    # TODO: There are a lot of functions in the Python 2 version that may or may not be used.
    #       Instead of porting them all over, we should just port them as they are needed.
    #       And rewrite things that can be done better in Python 3.

    # @classmethod
    # async def get_count(cls, owner: str, stage: Stage, status: Status):
    #     return await cls.count(
    #         cls.owner == owner, cls.stage == stage, cls.status == status
    #     )

    @classmethod
    @deprecated("Use HostDoc.find_one(HostDoc.ip == ip) instead.")
    async def get_by_ip(cls, ip: IPv4Address):
        return await cls.find_one(cls.ip == ip)

    # @classmethod
    # @deprecated("Use HostDoc.find_one(HostDoc.ip == ip).owner instead.")
    # async def get_owner_of_ip(cls, ip: IPv4Address):
    #     host = await cls.get_by_ip(ip)
    #     return host.owner

    # @classmethod
    # async def get_some_for_stage(
    #     cls,
    #     stage: Stage,
    #     count: int,
    #     owner: Optional[str] = None,
    #     waiting: bool = False,
    # ):
    #     if waiting:
    #         status = {"$in": [Status.READY, Status.WAITING]}
    #     else:
    #         status = Status.READY

    #     query = cls.find(cls.status == status, cls.stage == stage)
    #     if owner is not None:
    #         query = query.find(cls.owner == owner)

    #     # Sorting and limiting the results
    #     results = await query.sort([("priority", 1), ("r", 1)]).limit(count).to_list()
    #     return results
