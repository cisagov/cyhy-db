from beanie import Document
from datetime import datetime
from pydantic import Field
from typing import Optional
import asyncio

from .enum import ControlAction, ControlTarget
from ..utils import utcnow

CONTROL_DOC_POLL_INTERVAL = 5  # seconds


class SystemControlDoc(Document):
    action: ControlAction
    sender: str  # Free-form, for UI / Logging
    target: ControlTarget
    reason: str  # Free-form, for UI / Logging
    time: datetime = Field(default_factory=utcnow)  # creation time
    completed: bool = False  # Set to True when after the action has occurred

    class Settings:
        name = "control"

    @classmethod
    async def wait_for_completion(cls, document_id, timeout: Optional[int] = None):
        """Wait for this control action to complete. If a timeout is set, only wait a maximum of timeout seconds.
        Returns True if the document was completed, False otherwise."""
        start_time = utcnow()
        while True:
            doc = await cls.get(document_id)
            if doc.completed:
                return True
            if timeout and (utcnow() - start_time).total_seconds() > timeout:
                return False
            await asyncio.sleep(CONTROL_DOC_POLL_INTERVAL)
