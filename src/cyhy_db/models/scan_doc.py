# Standard Python Libraries
import datetime
import ipaddress
from typing import Any, Dict, Iterable

# Third-Party Libraries
from beanie import Document, Link
from beanie.operators import Push, Set
from pydantic import Field, model_validator
from pymongo import ASCENDING, IndexModel


class ScanDoc(Document):
    ip: ipaddress.IPv4Address = Field(...)
    ip_int: int = Field(...)
    latest: bool = Field(default=True)
    owner: str = Field(...)
    snapshots: list[Link["SnapshotDoc"]] = Field(default=[])
    source: str = Field(...)
    time: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    @model_validator(mode="before")
    def calculate_ip_int(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # ip may still be string if it was just set
        values["ip_int"] = int(ipaddress.ip_address(values["ip"]))
        return values

    class Config:
        # Pydantic configuration
        # Validate on assignment so ip_int is recalculated as ip is set
        validate_assignment = True

    class Settings:
        # Beanie settings
        name = "scandocs"
        indexes = [
            IndexModel(
                [("latest", ASCENDING), ("ip_int", ASCENDING)], name="latest_ip"
            ),
            IndexModel([("time", ASCENDING), ("owner", ASCENDING)], name="time_owner"),
            IndexModel([("int_ip", ASCENDING)], name="int_ip"),
            IndexModel([("snapshots", ASCENDING)], name="snapshots", sparse=True),
        ]

    @classmethod
    async def reset_latest_flag_by_owner(cls, owner):
        await cls.find(cls.latest == True, cls.owner == owner).update(
            Set({cls.latest: False})
        )

    @classmethod
    async def reset_latest_flag_by_ip(cls, ips):
        ip_ints = (
            [int(ipaddress.ip_address(x)) for x in ips]
            if isinstance(ips, Iterable)
            else [int(ipaddress.ip_address(ips))]
        )
        await cls.find(cls.latest == True, cls.ip_int.in_(ip_ints)).update(
            Set({cls.latest: False})
        )

    @classmethod
    async def tag_latest(cls, owners, snapshot_oid):
        await cls.find(cls.latest == True, cls.owner.in_(owners)).update(
            Push({cls.snapshots: snapshot_oid})
        )
