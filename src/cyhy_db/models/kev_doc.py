from beanie import Document


class KEVDoc(Document):
    id: str  # CVE
    known_ransomware: bool

    class Settings:
        name = "kevs"
