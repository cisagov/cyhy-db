"""The model for CVE (Common Vulnerabilities and Exposures) documents."""

# Standard Python Libraries
from typing import Any

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
    # See: https://github.com/cisagov/cyhy-db/issues/7
    # CVE ID as a string
    id: str = Indexed(primary_field=True)  # type: ignore[assignment]
    severity: int = Field(ge=1, le=4, default=1)

    @model_validator(mode="before")
    def calculate_severity(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Calculate CVE severity based on the CVSS score and version."""
        # A "before" validator sees the raw input, so field defaults have not been
        # applied yet and cvss_version can be absent even though it has one.
        #
        # The annotation says dict because that is what pydantic passes for the
        # ordinary construction and validation paths, and it is the useful thing
        # to tell a reader. It is not a guarantee: a "before" model validator is
        # handed whatever the caller supplied, so a model copy or an update can
        # arrive as something else. Widening this to Any would describe the edge
        # case at the cost of the common one, so the annotation stays and the
        # guard below returns anything that is not a dict untouched.
        #
        # Copilot has flagged the mismatch between the two on review before; it
        # is deliberate.
        if not isinstance(values, dict):
            return values

        # cvss_score is also raw here, and pydantic will happily coerce a string
        # or a Decimal into the float field, so convert the same way it does
        # rather than testing the type. A missing or non-numeric score is left to
        # pydantic, which reports it as a validation error instead of this
        # raising KeyError or TypeError.
        try:
            score = float(values["cvss_score"])
        except (KeyError, TypeError, ValueError):
            return values

        version = values.get("cvss_version", CVSSVersion.V3_1)

        if version == CVSSVersion.V2:
            if score == 10:
                values["severity"] = 4
            elif score >= 7.0:
                values["severity"] = 3
            elif score >= 4.0:
                values["severity"] = 2
            else:
                values["severity"] = 1
        else:  # CVSS versions 3.0 or 3.1
            if score >= 9.0:
                values["severity"] = 4
            elif score >= 7.0:
                values["severity"] = 3
            elif score >= 4.0:
                values["severity"] = 2
            else:
                values["severity"] = 1
        return values

    class Settings:
        """Beanie settings."""

        name = "cves"
