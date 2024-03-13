# Standard Python Libraries
from datetime import datetime
from ipaddress import IPv4Address, ip_address
from typing import Any, Dict, Iterable, List, Union

# Third-Party Libraries
from beanie import Document, Link
from beanie.operators import In, Push, Set
from bson import ObjectId
from bson.dbref import DBRef
from pydantic import ConfigDict, Field, model_validator
from pymongo import ASCENDING, IndexModel


class ScanDoc(Document):
    # Validate on assignment so ip_int is recalculated as ip is set
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    ip: IPv4Address = Field(...)
    ip_int: int = Field(...)
    latest: bool = Field(default=True)
    owner: str = Field(...)
    snapshots: List[Link["SnapshotDoc"]] = Field(default=[])
    source: str = Field(...)
    time: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="before")
    def calculate_ip_int(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # ip may still be string if it was just set
        values["ip_int"] = int(ip_address(values["ip"]))
        return values

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
    async def reset_latest_flag_by_owner(cls, owner: str):
        await cls.find(cls.latest == True, cls.owner == owner).update_many(
            Set({cls.latest: False})
        )

    @classmethod
    async def reset_latest_flag_by_ip(
        cls,
        ips: (
            int
            | IPv4Address
            | Iterable[int]
            | Iterable[IPv4Address]
            | Iterable[str]
            | str
        ),
    ):
        if isinstance(ips, Iterable):
            # TODO Figure out why coverage thinks this next line can exit early
            ip_ints = [int(ip_address(x)) for x in ips]
        else:
            ip_ints = [int(ip_address(ips))]

        await cls.find(cls.latest == True, In(cls.ip_int, ip_ints)).update_many(
            Set({cls.latest: False})
        )

    @classmethod
    async def tag_latest(
        cls, owners: List[str], snapshot: Union["SnapshotDoc", ObjectId, str]
    ):
        from . import SnapshotDoc

        if isinstance(snapshot, SnapshotDoc):
            ref = DBRef(SnapshotDoc.Settings.name, snapshot.id)
        elif isinstance(snapshot, ObjectId):
            ref = DBRef(SnapshotDoc.Settings.name, snapshot)
        elif isinstance(snapshot, str):
            ref = DBRef(SnapshotDoc.Settings.name, ObjectId(snapshot))
        else:
            raise ValueError("Invalid snapshot type")
        await cls.find(cls.latest == True, In(cls.owner, owners)).update_many(
            Push({cls.snapshots: ref})
        )
