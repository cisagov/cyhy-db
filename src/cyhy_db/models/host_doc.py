"""The model for CyHy host documents."""

# Standard Python Libraries
from datetime import datetime
from ipaddress import IPv4Address, ip_address
import random
from typing import Any, Dict, Optional, Tuple

# Third-Party Libraries
from beanie import Document, Insert, Replace, ValidateOnSave, before_event
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pymongo import ASCENDING, IndexModel

from ..utils import deprecated, utcnow
from .enum import Stage, Status


class State(BaseModel):
    """The state of a host."""

    reason: str
    up: bool


class HostDoc(Document):
    """The host document model."""

    model_config = ConfigDict(extra="forbid")

    # See: https://github.com/cisagov/cyhy-db/issues/7
    # IP address as an integer
    id: int = Field(default_factory=int)  # type: ignore[assignment]
    ip: IPv4Address = Field(...)
    last_change: datetime = Field(default_factory=utcnow)
    latest_scan: Dict[Stage, datetime] = Field(default_factory=dict)
    loc: Optional[Tuple[float, float]] = Field(default=None)
    next_scan: Optional[datetime] = Field(default=None)
    owner: str = Field(...)
    priority: int = Field(default=0)
    r: float = Field(default_factory=random.random)
    stage: Stage = Field(default=Stage.NETSCAN1)
    state: State = Field(default_factory=lambda: State(reason="new", up=False))
    status: Status = Field(default=Status.WAITING)

    @model_validator(mode="before")
    def calculate_ip_int(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the integer representation of an IP address."""
        # ip may still be string if it was just set
        values["_id"] = int(ip_address(values["ip"]))
        return values

    @before_event(Insert, Replace, ValidateOnSave)
    async def before_save(self):
        """Set data just prior to saving a host document."""
        self.last_change = utcnow()

    class Settings:
        """Beanie settings."""

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
        """Set state.up based on different stage evidence.

        nmap has a concept of up which is different from our definition. An nmap
        "up" just means it got a reply, not that there are any open ports. Note
        either argument can be None.
        """
        if has_open_ports:  # Only PORTSCAN sends in has_open_ports
            self.state = State(up=True, reason="open-port")
        elif has_open_ports is False:
            self.state = State(up=False, reason="no-open")
        elif nmap_says_up is False:  # NETSCAN says host is down
            self.state = State(up=False, reason=reason)

    # TODO: There are a lot of functions in the Python 2 version that may or may not be used.
    #       Instead of porting them all over, we should just port them as they are needed.
    #       And rewrite things that can be done better in Python 3.

    @classmethod
    @deprecated("Use HostDoc.find_one(HostDoc.ip == ip) instead.")
    async def get_by_ip(cls, ip: IPv4Address):
        """Return a host document with the given IP address."""
        return await cls.find_one(cls.ip == ip)
