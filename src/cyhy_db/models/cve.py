from odmantic import Model, Field
from pydantic import ValidationInfo, field_validator
from typing import Literal

class CVE(Model):
    id: str = Field(primary_field=True)
    cvss_score: float
    cvss_version: Literal["2.0", "3.0", "3.1"]
    severity: Literal[1,2,3,4] = Field(default_factory=lambda: 1)

    model_config = {
        "collection": "cves"
    }

    @field_validator("cvss_score")
    def validate_cvss_score(cls, v: float) -> float:
        if v < 0.0 or v > 10.0:
            raise ValueError("CVSS score must be between 0.0 and 10.0 inclusive")
        return v
    
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
        else: # 3.0 or 3.1
            if self.cvss_score >= 9.0:
                self.severity = 4
            elif self.cvss_score >= 7.0:
                self.severity = 3
            elif self.cvss_score >= 4.0:
                self.severity = 2
            else:
                self.severity = 1

    async def save(self, engine):
        self.calculate_severity()
        await engine.save(self)
