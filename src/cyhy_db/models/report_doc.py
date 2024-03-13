# Standard Python Libraries
from datetime import datetime
from typing import List

# Third-Party Libraries
from beanie import Document, Indexed, Link
from pydantic import ConfigDict, Field
from pymongo import ASCENDING, IndexModel

from . import SnapshotDoc
from ..utils import utcnow
from .enum import ReportType


class ReportDoc(Document):
    model_config = ConfigDict(extra="forbid")

    owner: str
    generated_time: datetime = Field(default_factory=utcnow)
    snapshots: List[Link[SnapshotDoc]]
    report_types: List[ReportType]

    class Settings:
        name = "reports"
        indexes = [
            IndexModel(
                [
                    ("owner", ASCENDING),
                ],
                name="owner",
            ),
            IndexModel(
                [
                    ("generated_time", ASCENDING),
                ],
                name="generated_time",
            ),
        ]
