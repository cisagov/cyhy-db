"""Test ScanDoc model functionality."""

import ipaddress

# Third-Party Libraries
import pytest
from pydantic import ValidationError

# cisagov Libraries
from cyhy_db.models import ScanDoc


VALID_IP_1_STR = "0.0.0.1"
VALID_IP_2_STR = "0.0.0.2"
VALID_IP_1_INT = int(ipaddress.ip_address(VALID_IP_1_STR))
VALID_IP_2_INT = int(ipaddress.ip_address(VALID_IP_2_STR))


def test_ip_int_init():
    # Create a ScanDoc object
    scan_doc = ScanDoc(
        ip=ipaddress.ip_address(VALID_IP_1_STR),
        owner="YOUR_MOM",
        source="nmap",
    )

    assert scan_doc.ip_int == int(
        ipaddress.ip_address(VALID_IP_1_STR)
    ), "IP address integer was not calculated correctly on init"


def test_ip_int_change():
    # Create a ScanDoc object
    scan_doc = ScanDoc(
        ip=ipaddress.ip_address(VALID_IP_1_STR),
        owner="YOUR_MOM",
        source="nmap",
    )

    scan_doc.ip = ipaddress.ip_address(VALID_IP_2_STR)

    assert scan_doc.ip_int == int(
        ipaddress.ip_address(VALID_IP_2_STR)
    ), "IP address integer was not calculated correctly on change"


def test_ip_string_set():
    scan_doc = ScanDoc(
        ip=VALID_IP_1_STR,
        owner="YOUR_MOM",
        source="nmap",
    )

    assert type(scan_doc.ip) == ipaddress.IPv4Address, "IP address was not converted"
    assert scan_doc.ip_int == VALID_IP_1_INT, "IP address integer was not calculated"


async def test_ip_address_field_fetch():
    # Create a ScanDoc object
    scan_doc = ScanDoc(
        ip=ipaddress.ip_address(VALID_IP_1_STR),
        owner="YOUR_MOM",
        source="nmap",
    )

    # Save the ScanDoc object to the database
    await scan_doc.save()

    # Retrieve the ScanDoc object from the database
    retrieved_doc = await ScanDoc.get(scan_doc.id)

    # Assert that the retrieved IP address is equal to the one we saved
    assert retrieved_doc.ip == ipaddress.ip_address(
        VALID_IP_1_STR
    ), "IP address does not match"

    assert retrieved_doc.ip_int == VALID_IP_1_INT, "IP address integer does not match"


def test_invalid_ip_address():
    with pytest.raises(ValidationError):
        ScanDoc(
            ip="999.999.999.999",  # This should be invalid
            owner="owner_example",
            source="source_example",
        )


async def test_reset_latest_flag_by_owner():
    # Create a ScanDoc object
    scan_doc = ScanDoc(
        ip=ipaddress.ip_address(VALID_IP_1_STR), owner="RESET_MY_LATEST", source="nmap"
    )
    await scan_doc.save()
    # Check that the latest flag is set to True
    assert scan_doc.latest == True
    # Reset the latest flag
    await ScanDoc.reset_latest_flag_by_owner("RESET_MY_LATEST")
    # Retrieve the ScanDoc object from the database
    await scan_doc.sync()
    # Check that the latest flag is set to False
    assert scan_doc.latest == False
