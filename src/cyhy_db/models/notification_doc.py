"""The model for notification documents."""

# Standard Python Libraries
from typing import List

# Third-Party Libraries
from beanie import BeanieObjectId, Document
from pydantic import ConfigDict, Field


class NotificationDoc(Document):
    """The notification document model."""

    model_config = ConfigDict(extra="forbid")

    generated_for: List[str] = Field(
        default=[]
    )  # list of owners built as notifications are generated
    ticket_id: BeanieObjectId = Field(...)  # ticket id that triggered the notification
    ticket_owner: str  # owner of the ticket

    class Settings:
        """Beanie settings."""

        name = "notifications"
