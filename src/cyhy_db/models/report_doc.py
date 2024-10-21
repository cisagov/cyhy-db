"""The model for CyHy report documents."""

# Standard Python Libraries
from datetime import datetime
from typing import List

# Third-Party Libraries
from beanie import Document, Link
from pydantic import ConfigDict, Field
from pymongo import ASCENDING, IndexModel

from . import SnapshotDoc
from ..utils import utcnow
from .enum import ReportType


class ReportDoc(Document):
    """The report document model."""

    model_config = ConfigDict(extra="forbid")

    generated_time: datetime = Field(default_factory=utcnow)
    owner: str
    report_types: List[ReportType]
    snapshots: List[Link[SnapshotDoc]]

    class Settings:
        """Beanie settings."""

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
