"""The model for CVE (Common Vulnerabilities and Exposures) documents."""

# Standard Python Libraries
from typing import Any, Dict

# Third-Party Libraries
from beanie import Document, Indexed
from pydantic import ConfigDict, Field, model_validator

from .enum import CVSSVersion


class CVEDoc(Document):
    """The CVE document model."""

    # Validate on assignment so severity is calculated
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    cvss_score: float = Field(ge=0.0, le=10.0)
    cvss_version: CVSSVersion = Field(default=CVSSVersion.V3_1)
    # CVE ID as a string
    id: str = Indexed(primary_field=True)  # type: ignore[assignment]
    severity: int = Field(ge=1, le=4, default=1)

    @model_validator(mode="before")
    def calculate_severity(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate CVE severity based on the CVSS score and version."""
        if values["cvss_version"] == CVSSVersion.V2:
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

    class Settings:
        """Beanie settings."""

        name = "cves"
