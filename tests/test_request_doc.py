"""Test RequestDoc model functionality."""

# Standard Python Libraries
from datetime import time

# Third-Party Libraries
import pytest

# cisagov Libraries
from cyhy_db.models import RequestDoc
from cyhy_db.models.enum import ScanType
from cyhy_db.models.request_doc import Agency, ScanLimit, Window


async def test_init():
    """Test RequestDoc object initialization."""
    # Create a RequestDoc object
    request_doc = RequestDoc(
        agency=Agency(
            name="Cybersecurity and Infrastructure Security Agency", acronym="CISA"
        )
    )

    await request_doc.save()

    # Verify that the id was set to the acronym
    assert (
        request_doc.id == request_doc.agency.acronym
    ), "id was not correctly set to agency acronym"


def test_parse_time_valid_time_str():
    """Test the parse_time validator with valid string input."""
    valid_time_str = "12:34:56"
    parsed_time = Window.parse_time(valid_time_str)
    assert parsed_time == time(12, 34, 56), "Failed to parse valid time string"


def test_parse_time_invalid_time_str():
    """Test the parse_time validator with invalid string input."""
    invalid_time_str = "invalid_time"
    with pytest.raises(
        ValueError,
        match="time data 'invalid_time' does not match format '%H:%M:%S'",
    ):
        Window.parse_time(invalid_time_str)


def test_parse_time_valid_time_obj():
    """Test the parse_time validator with valid time input."""
    valid_time_obj = time(12, 34, 56)
    parsed_time = Window.parse_time(valid_time_obj)
    assert parsed_time == valid_time_obj, "Failed to parse valid time object"


def test_parse_time_invalid_type():
    """Test the parse_time validator with an invalid input type."""
    invalid_time_type = 12345
    with pytest.raises(
        ValueError,
        match="Invalid time format. Expected a string in '%H:%M:%S' format or datetime.time instance.",
    ):
        Window.parse_time(invalid_time_type)


async def test_scan_limit():
    """Test the ScanLimit model."""
    # Create a RequestDoc object
    request_doc = RequestDoc(
        agency=Agency(name="Office of Fragile Networking", acronym="OFN")
    )

    scan_limit = ScanLimit(scan_type=ScanType.CYHY, concurrent=1)
    assert scan_limit.scan_type == ScanType.CYHY, "Scan type was not set correctly"
    assert scan_limit.concurrent == 1, "Concurrent was not set correctly"

    request_doc.scan_limits.append(scan_limit)
    assert (
        request_doc.scan_limits[0].scan_type == ScanType.CYHY
    ), "Scan type was not set correctly"
    await request_doc.save()

    # TODO complete this test
