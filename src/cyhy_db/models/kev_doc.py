from beanie import Document
from pydantic import ConfigDict


class KEVDoc(Document):
    model_config = ConfigDict(extra="forbid")

    id: str  # CVE
    known_ransomware: bool

    class Settings:
        name = "kevs"
