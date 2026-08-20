"""Test CVE model functionality."""

# Third-Party Libraries
from pydantic import ValidationError
import pytest

# cisagov Libraries
from cyhy_db.models import CVEDoc
from cyhy_db.models.enum import CVSSVersion

severity_params = [
    (CVSSVersion.V2, 10, 4),
    (CVSSVersion.V2, 7.0, 3),
    (CVSSVersion.V2, 4.0, 2),
    (CVSSVersion.V2, 0.0, 1),
    (CVSSVersion.V3, 9.0, 4),
    (CVSSVersion.V3, 7.0, 3),
    (CVSSVersion.V3, 4.0, 2),
    (CVSSVersion.V3, 0.0, 1),
    (CVSSVersion.V3_1, 9.0, 4),
    (CVSSVersion.V3_1, 7.0, 3),
    (CVSSVersion.V3_1, 4.0, 2),
    (CVSSVersion.V3_1, 0.0, 1),
]


def test_calculate_severity_passes_non_dict_through():
    """Test that non-dict input is returned unchanged."""
    sentinel = object()
    result = CVEDoc.calculate_severity(sentinel)
    assert result is sentinel


@pytest.mark.parametrize("version, score, expected_severity", severity_params)
def test_calculate_severity(version, score, expected_severity):
    """Test that the severity is calculated correctly."""
    cve = CVEDoc(id="CVE-2024-0128", cvss_version=version, cvss_score=score)
    assert (
        cve.severity == expected_severity
    ), f"Failed for CVSS {version} with score {score}"


@pytest.mark.parametrize("bad_score", [-1.0, 11.0])
def test_invalid_cvss_score(bad_score):
    """Test that an invalid CVSS score raises a ValueError."""
    with pytest.raises(ValidationError):
        CVEDoc(cvss_version=CVSSVersion.V3_1, cvss_score=bad_score, id="test-cve")


async def test_save():
    """Test that the severity is calculated correctly on save."""
    cve = CVEDoc(cvss_version=CVSSVersion.V3_1, cvss_score=9.0, id="test-cve")
    await cve.save()  # Saving the object
    saved_cve = await CVEDoc.get("test-cve")  # Retrieving the object

    assert saved_cve is not None, "CVE not saved correctly"
    assert saved_cve.severity == 4, "Severity not calculated correctly on save"


# calculate_severity is a "before" validator, so it runs on the raw input before
# pydantic applies field defaults. These call it directly, which keeps them off
# the database and exercises the exact spot where cvss_version may be missing.

severity_default_version_params = [
    (9.8, 4),
    (7.0, 3),
    (4.0, 2),
    (0.0, 1),
]


@pytest.mark.parametrize("score, expected_severity", severity_default_version_params)
def test_calculate_severity_without_cvss_version(score, expected_severity):
    """Test that an omitted CVSS version falls back to the field default."""
    values = CVEDoc.calculate_severity({"id": "CVE-2024-0128", "cvss_score": score})
    assert values["severity"] == expected_severity


def test_calculate_severity_on_stored_document():
    """Test a stored document that predates the cvss_version field."""
    values = CVEDoc.calculate_severity({"_id": "CVE-2024-0128", "cvss_score": 9.8})
    assert values["severity"] == 4


def test_calculate_severity_leaves_a_missing_score_alone():
    """Test that a missing CVSS score is left for pydantic to report."""
    values = CVEDoc.calculate_severity({"id": "CVE-2024-0128"})
    assert "severity" not in values


def test_calculate_severity_with_raw_string_v2():
    """Test that a raw string cvss_version matches the V2 enum."""
    values = CVEDoc.calculate_severity(
        {"id": "CVE-2024-0128", "cvss_version": "2.0", "cvss_score": 10}
    )
    assert values["severity"] == 4


def test_missing_cvss_score_raises_validation_error():
    """Test that a missing CVSS score is a validation error, not a KeyError."""
    with pytest.raises(ValidationError):
        CVEDoc(id="CVE-2024-0128")
