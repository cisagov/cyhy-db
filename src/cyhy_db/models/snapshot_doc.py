# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from beanie import Document
from pydantic import Field
from pymongo import ASCENDING, IndexModel


class SnapshotDoc(Document):
    owner: str = Field(...)
    start_time: datetime = Field(...)
    end_time: datetime = Field(...)

    class Settings:
        # Beanie settings
        name = "snapshots"
        indexes = [
            IndexModel(
                [
                    ("owner", ASCENDING),
                    ("start_time", ASCENDING),
                    ("end_time", ASCENDING),
                ],
                name="uniques",
                unique=True,
            ),
            IndexModel(
                [("latest", ASCENDING), ("owner", ASCENDING)], name="latest_owner"
            ),
        ]
