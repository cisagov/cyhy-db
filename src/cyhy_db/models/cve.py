# Third-Party Libraries
from beanie import Document, Indexed, ValidateOnSave, before_event
from pydantic import Field


class CVE(Document):
    id: str = Indexed(primary_field=True)  # CVE ID
    cvss_score: float = Field(ge=0.0, le=10.0)
    cvss_version: str = Field(enum=["2.0", "3.0", "3.1"])
    severity: int = Field(ge=1, le=4, default=1)

    class Settings:
        name = "cves"

    @before_event(ValidateOnSave)
    def calculate_severity(self):
        if self.cvss_version == "2.0":
            if self.cvss_score == 10:
                self.severity = 4
            elif self.cvss_score >= 7.0:
                self.severity = 3
            elif self.cvss_score >= 4.0:
                self.severity = 2
            else:
                self.severity = 1
        else:  # CVSS versions 3.0 or 3.1
            if self.cvss_score >= 9.0:
                self.severity = 4
            elif self.cvss_score >= 7.0:
                self.severity = 3
            elif self.cvss_score >= 4.0:
                self.severity = 2
            else:
                self.severity = 1
