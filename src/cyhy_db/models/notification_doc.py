from beanie import Document, BeanieObjectId
from pydantic import Field, BaseModel, ConfigDict
from bson import ObjectId
from typing import List


class NotificationDoc(Document):
    model_config = ConfigDict(extra="forbid")

    ticket_id: BeanieObjectId = Field(...)  # ticket id that triggered the notification
    ticket_owner: str  # owner of the ticket
    generated_for: List[str] = Field(
        default=[]
    )  # list of owners built as notifications are generated

    class Settings:
        name = "notifications"
