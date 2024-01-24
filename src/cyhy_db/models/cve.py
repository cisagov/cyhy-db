"""This module defines the CVE model."""

# Standard Python Libraries
from typing import Literal

# Third-Party Libraries
from odmantic import Field, Model
from pydantic import field_validator


class CVE(Model):
    """This class represents the CVE model."""

    id: str = Field(primary_field=True)
    cvss_score: float
    cvss_version: Literal["2.0", "3.0", "3.1"]
    severity: Literal[1, 2, 3, 4] = Field(default_factory=lambda: 1)

    model_config = {"collection": "cves"}

    @field_validator("cvss_score")
    def validate_cvss_score(cls, v: float) -> float:
        """Validate the CVSS score."""
        if v < 0.0 or v > 10.0:
            raise ValueError("CVSS score must be between 0.0 and 10.0 inclusive")
        return v

    def calculate_severity(self):
        """Calculate the severity from the CVSS score."""
        # Calculate severity from cvss on save
        # Source: https://nvd.nist.gov/vuln-metrics/cvss
        #
        # Notes:
        # - The CVSS score to severity mapping is not continuous (e.g. a
        #   score of 8.95 is undefined according to their table).  However,
        #   the CVSS equation documentation
        #   (https://www.first.org/cvss/specification-document#CVSS-v3-1-Equations)
        #   specifies that all CVSS scores are rounded up to the nearest tenth
        #   of a point, so our severity mapping below is valid.
        # - CVSSv3 specifies that a score of 0.0 has a severity of "None", but
        #   we have chosen to map 0.0 to severity 1 ("Low") because CyHy code
        #   has historically assumed severities between 1 and 4 (inclusive).
        #   Since we have not seen CVSSv3 scores lower than 3.1, this will
        #   hopefully never be an issue.
        if self.cvss_version == "2.0":
            if self.cvss_score == 10:
                self.severity = 4
            elif self.cvss_score >= 7.0:
                self.severity = 3
            elif self.cvss_score >= 4.0:
                self.severity = 2
            else:
                self.severity = 1
        else:  # 3.0 or 3.1
            if self.cvss_score >= 9.0:
                self.severity = 4
            elif self.cvss_score >= 7.0:
                self.severity = 3
            elif self.cvss_score >= 4.0:
                self.severity = 2
            else:
                self.severity = 1

    async def save(self, engine):
        """Save the CVE to the database."""
        self.calculate_severity()
        await engine.save(self)
