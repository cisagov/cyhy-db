from beanie import Document, Indexed, Link
from datetime import datetime
from typing import List
from pymongo import ASCENDING, IndexModel
from pydantic import Field, ConfigDict

from . import SnapshotDoc
from .enum import ReportType
from ..utils import utcnow


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
