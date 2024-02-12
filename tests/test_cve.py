"""Test CVE model functionality."""

# Third-Party Libraries
from pydantic import ValidationError
import pytest

# cisagov Libraries
from cyhy_db.models import CVE

severity_params = [
    ("2.0", 10, 4),
    ("2.0", 7.0, 3),
    ("2.0", 4.0, 2),
    ("2.0", 0.0, 1),
    ("3.0", 9.0, 4),
    ("3.0", 7.0, 3),
    ("3.0", 4.0, 2),
    ("3.0", 0.0, 1),
    ("3.1", 9.0, 4),
    ("3.1", 7.0, 3),
    ("3.1", 4.0, 2),
    ("3.1", 0.0, 1),
]


@pytest.mark.parametrize("version, score, expected_severity", severity_params)
def test_calculate_severity(version, score, expected_severity):
    """Test that the severity is calculated correctly."""
    cve = CVE(id="CVE-2024-0128", cvss_version=version, cvss_score=score)
    assert (
        cve.severity == expected_severity
    ), f"Failed for CVSS {version} with score {score}"


@pytest.mark.parametrize("bad_score", [-1.0, 11.0])
def test_invalid_cvss_score(bad_score):
    """Test that an invalid CVSS score raises a ValueError."""
    with pytest.raises(ValidationError):
        CVE(cvss_version="3.1", cvss_score=bad_score, id="test-cve")


async def test_save():
    """Test that the severity is calculated correctly on save."""
    cve = CVE(cvss_version="3.1", cvss_score=9.0, id="test-cve")
    await cve.save()  # Saving the object
    saved_cve = await CVE.get("test-cve")  # Retrieving the object

    assert saved_cve is not None, "CVE not saved correctly"
    assert saved_cve.severity == 4, "Severity not calculated correctly on save"
