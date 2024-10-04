"""The model for CyHy ticket documents."""

# Third-Party Libraries
from beanie import Document
from pymongo import ASCENDING, IndexModel


class TicketDoc(Document):
    """The ticket document model."""

    pass

    class Settings:
        """Beanie settings."""

        name = "tickets"

        indexes = [
            IndexModel(
                [
                    ("ip_int", ASCENDING),
                    ("port", ASCENDING),
                    ("protocol", ASCENDING),
                    ("source", ASCENDING),
                    ("source_id", ASCENDING),
                    ("open", ASCENDING),
                    ("false_positive", ASCENDING),
                ],
                name="ip_port_protocol_source_open_false_positive",
            ),
            IndexModel(
                [("ip_int", ASCENDING), ("open", ASCENDING)],
                name="ip_open",
            ),
            IndexModel(
                [("open", ASCENDING), ("owner", ASCENDING)],
                name="open_owner",
            ),
            IndexModel(
                [("time_opened", ASCENDING), ("open", ASCENDING)],
                name="time_opened",
            ),
            IndexModel(
                [("last_change", ASCENDING)],
                name="last_change",
            ),
            IndexModel(
                [("time_closed", ASCENDING)],
                name="time_closed",
                sparse=True,
            ),
        ]
