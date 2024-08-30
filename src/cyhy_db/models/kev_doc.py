"""The model for KEV (Known Exploited Vulnerabilities) documents."""

# Third-Party Libraries
from beanie import Document
from pydantic import ConfigDict, Field


class KEVDoc(Document):
    """The KEV document model."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=str)  # type: ignore[assignment]
    known_ransomware: bool

    class Settings:
        """Beanie settings."""

        name = "kevs"
