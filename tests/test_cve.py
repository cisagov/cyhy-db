"""Test CVE model functionality."""

# Third-Party Libraries
import pytest

# cisagov Libraries
from cyhy_db.models.cve import CVE

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
    cve = CVE(cvss_version=version, cvss_score=score, id="test-cve")
    cve.calculate_severity()
    assert (
        cve.severity == expected_severity
    ), f"Failed for CVSS {version} with score {score}"


def test_invalid_cvss_score():
    """Test that an invalid CVSS score raises a ValueError."""
    with pytest.raises(
        ValueError, match="CVSS score must be between 0.0 and 10.0 inclusive"
    ):
        CVE(cvss_version="3.1", cvss_score=11.0, id="test-cve")


@pytest.mark.asyncio
async def test_save(mongodb_engine):
    """Test that the severity is calculated correctly on save."""
    cve = CVE(cvss_version="3.1", cvss_score=9.0, id="test-cve")
    await cve.save(mongodb_engine)
    saved_cve = await mongodb_engine.find_one(CVE, CVE.id == "test-cve")
    assert saved_cve is not None, "CVE not saved correctly"
    assert saved_cve.severity == 4, "Severity not calculated correctly on save"
