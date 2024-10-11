"""The model for CyHy system control documents."""

# Standard Python Libraries
import asyncio
from datetime import datetime
from typing import Optional

# Third-Party Libraries
from beanie import Document
from pydantic import ConfigDict, Field

from ..utils import utcnow
from .enum import ControlAction, ControlTarget

CONTROL_DOC_POLL_INTERVAL = 5  # seconds


class SystemControlDoc(Document):
    """The system control document model."""

    model_config = ConfigDict(extra="forbid")

    action: ControlAction
    completed: bool = False  # Set to True when after the action has occurred
    reason: str  # Free-form, for UI / Logging
    sender: str  # Free-form, for UI / Logging
    target: ControlTarget
    time: datetime = Field(default_factory=utcnow)  # creation time

    class Settings:
        """Beanie settings."""

        name = "control"

    @classmethod
    async def wait_for_completion(cls, document_id, timeout: Optional[int] = None):
        """Wait for this control action to complete.

        If a timeout is set, only wait a maximum of timeout seconds.
        Returns True if the document was completed, False otherwise.
        """
        start_time = utcnow()
        while True:
            doc = await cls.get(document_id)
            if doc and doc.completed:
                return True
            if timeout and (utcnow() - start_time).total_seconds() > timeout:
                return False
            await asyncio.sleep(CONTROL_DOC_POLL_INTERVAL)
