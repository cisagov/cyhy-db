# Third-Party Libraries
from beanie import Document, Indexed, ValidateOnSave, before_event
from pydantic import Field, model_validator
from .enum import CVSSVersion
from typing import Any, Dict


class CVE(Document):
    id: str = Indexed(primary_field=True)  # CVE ID
    cvss_score: float = Field(ge=0.0, le=10.0)
    cvss_version: CVSSVersion = Field(default=CVSSVersion.V3_1)
    severity: int = Field(ge=1, le=4, default=1)

    @model_validator(mode="before")
    def calculate_severity(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if values["cvss_version"] == "2.0":
            if values["cvss_score"] == 10:
                values["severity"] = 4
            elif values["cvss_score"] >= 7.0:
                values["severity"] = 3
            elif values["cvss_score"] >= 4.0:
                values["severity"] = 2
            else:
                values["severity"] = 1
        else:  # CVSS versions 3.0 or 3.1
            if values["cvss_score"] >= 9.0:
                values["severity"] = 4
            elif values["cvss_score"] >= 7.0:
                values["severity"] = 3
            elif values["cvss_score"] >= 4.0:
                values["severity"] = 2
            else:
                values["severity"] = 1
        return values

    class Config:
        # Pydantic configuration
        # Validate on assignment so ip_int is recalculated as ip is set
        validate_assignment = True

    class Settings:
        # Beanie settings
        name = "cves"
