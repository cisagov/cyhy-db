"""Test ScanDoc model functionality."""

# Standard Python Libraries
import ipaddress

# Third-Party Libraries
from pydantic import ValidationError
import pytest

# cisagov Libraries
from cyhy_db.models import ScanDoc, SnapshotDoc
from cyhy_db.utils import utcnow

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

    assert isinstance(scan_doc.ip, ipaddress.IPv4Address), "IP address was not converted"
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
    OWNER = "RESET_BY_OWNER"
    scan_doc = ScanDoc(
        ip=ipaddress.ip_address(VALID_IP_1_STR), owner=OWNER, source="nmap"
    )
    await scan_doc.save()
    # Check that the latest flag is set to True
    assert scan_doc.latest is True
    # Reset the latest flag
    await ScanDoc.reset_latest_flag_by_owner(OWNER)
    # Retrieve the ScanDoc object from the database
    await scan_doc.sync()
    # Check that the latest flag is set to False
    assert scan_doc.latest is False


async def test_reset_latest_flag_by_ip():
    # Create a ScanDoc object
    IP_TO_RESET_1 = ipaddress.ip_address("128.205.1.2")
    IP_TO_RESET_2 = ipaddress.ip_address("128.205.1.3")
    scan_doc_1 = ScanDoc(ip=IP_TO_RESET_1, owner="RESET_BY_IP", source="nmap")
    scan_doc_2 = ScanDoc(ip=IP_TO_RESET_2, owner="RESET_BY_IP", source="nmap")
    await scan_doc_1.save()
    await scan_doc_2.save()
    # Check that the latest flag is set to True
    assert scan_doc_1.latest is True
    # Reset the latest flag on single IP
    await ScanDoc.reset_latest_flag_by_ip(IP_TO_RESET_1)
    # Retrieve the ScanDoc object from the database
    await scan_doc_1.sync()
    # Check that the latest flag is set to False
    assert scan_doc_1.latest is False
    # Reset by both IPs
    await ScanDoc.reset_latest_flag_by_ip([IP_TO_RESET_1, IP_TO_RESET_2])
    # Retrieve the ScanDoc object from the database
    await scan_doc_2.sync()
    # Check that the latest flag is set to False
    assert scan_doc_2.latest is False


async def test_tag_latest():
    # Create a SnapshotDoc object

    owner = "TAG_LATEST"
    snapshot_doc = SnapshotDoc(
        owner=owner,
        start_time=utcnow(),
        end_time=utcnow(),
    )
    await snapshot_doc.save()
    # Create a ScanDoc object
    scan_doc = ScanDoc(
        ip=ipaddress.ip_address(VALID_IP_1_STR),
        owner=owner,
        source="nmap",
    )
    await scan_doc.save()

    # Tag the latest scan
    await ScanDoc.tag_latest([owner], snapshot_doc)

    # Retrieve the ScanDoc object from the database
    scan_doc = await ScanDoc.find_one(ScanDoc.id == scan_doc.id, fetch_links=True)

    # Check that the scan now has a snapshot
    assert scan_doc.snapshots == [snapshot_doc], "Snapshot not added to scan"
