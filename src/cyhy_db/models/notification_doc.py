# Standard Python Libraries
from typing import List

# Third-Party Libraries
from beanie import BeanieObjectId, Document
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class NotificationDoc(Document):
    model_config = ConfigDict(extra="forbid")

    ticket_id: BeanieObjectId = Field(...)  # ticket id that triggered the notification
    ticket_owner: str  # owner of the ticket
    generated_for: List[str] = Field(
        default=[]
    )  # list of owners built as notifications are generated

    class Settings:
        name = "notifications"
