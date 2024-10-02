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
    """Test IP address integer conversion on initialization.

    This test verifies that the IP address is correctly converted to an
    integer when a ScanDoc object is initialized.
    """
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
    """Test IP address integer conversion on IP address change.

    This test verifies that the IP address is correctly converted to an
    integer when the IP address of a ScanDoc object is changed.
    """
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
    """Test IP address string conversion and integer calculation.

    This test verifies that an IP address provided as a string is correctly
    converted to an ipaddress.IPv4Address object and that the corresponding
    integer value is calculated correctly.
    """
    scan_doc = ScanDoc(
        ip=VALID_IP_1_STR,
        owner="YOUR_MOM",
        source="nmap",
    )

    assert isinstance(
        scan_doc.ip, ipaddress.IPv4Address
    ), "IP address was not converted"
    assert scan_doc.ip_int == VALID_IP_1_INT, "IP address integer was not calculated"


async def test_ip_address_field_fetch():
    """Test IP address retrieval from the database.

    This test verifies that the IP address of a ScanDoc object is correctly
    retrieved from the database.
    """
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
    """Test validation error for invalid IP addresses.

    This test verifies that a ValidationError is raised when an invalid IP
    address is provided to a ScanDoc object.
    """
    with pytest.raises(ValidationError):
        ScanDoc(
            ip="999.999.999.999",  # This should be invalid
            owner="owner_example",
            source="source_example",
        )


async def test_reset_latest_flag_by_owner():
    """Test resetting the latest flag by owner.

    This test verifies that the latest flag of ScanDoc objects is correctly
    reset when the reset_latest_flag_by_owner method is called.
    """
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
    """Test resetting the latest flag by IP address.

    This test verifies that the latest flag of ScanDoc objects is correctly
    reset when the reset_latest_flag_by_ip method is called.
    """
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


async def test_tag_latest_snapshot_doc():
    """Test tagging the latest scan with a SnapshotDoc.

    This test verifies that the latest ScanDoc object is correctly tagged with a
    SnapshotDoc object when the tag_latest method is called with a SnapshotDoc.
    """
    # Create a SnapshotDoc object
    owner = "TAG_LATEST_SNAPSHOT_DOC"
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


async def test_tag_latest_snapshot_id():
    """Test tagging the latest scan with a snapshot ObjectId.

    This test verifies that the latest ScanDoc object is correctly tagged with a
    SnapshotDoc object when the tag_latest method is called with a snapshot
    ObjectId.
    """
    # Create a SnapshotDoc object
    owner = "TAG_LATEST_SNAPSHOT_ID"
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

    # Tag the latest scan with the snapshot id
    await ScanDoc.tag_latest([owner], snapshot_doc.id)

    # Retrieve the ScanDoc object from the database
    scan_doc = await ScanDoc.find_one(ScanDoc.id == scan_doc.id, fetch_links=True)

    # Check that the scan now has a snapshot
    assert scan_doc.snapshots == [snapshot_doc], "Snapshot not added to scan"


async def test_tag_latest_snapshot_id_str():
    """Test tagging the latest scan with the string representation of a snapshot ObjectId.

    This test verifies that the latest ScanDoc object is correctly tagged with a
    SnapshotDoc object when the tag_latest method is called with the string
    representation of a snapshot ObjectId.
    """
    # Create a SnapshotDoc object
    owner = "TAG_LATEST_SNAPSHOT_ID_STR"
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

    # Tag the latest scan with the string representation of the snapshot id
    await ScanDoc.tag_latest([owner], str(snapshot_doc.id))

    # Retrieve the ScanDoc object from the database
    scan_doc = await ScanDoc.find_one(ScanDoc.id == scan_doc.id, fetch_links=True)

    # Check that the scan now has a snapshot
    assert scan_doc.snapshots == [snapshot_doc], "Snapshot not added to scan"


async def test_tag_latest_invalid_type():
    """Test tagging the latest scan with an invalid object type."""
    owner = "TAG_LATEST_INVALID_TYPE"
    scan_doc = ScanDoc(
        ip=ipaddress.ip_address(VALID_IP_1_STR),
        owner=owner,
        source="nmap",
    )
    await scan_doc.save()

    with pytest.raises(ValueError, match="Invalid snapshot type"):
        # Attempt to tag the latest scan with an invalid object type
        await ScanDoc.tag_latest([owner], 12345)

    # Retrieve the ScanDoc object from the database
    scan_doc = await ScanDoc.find_one(ScanDoc.id == scan_doc.id, fetch_links=True)

    # Confirm that the scan does not have a snapshot
    assert scan_doc.snapshots == [], "Scan should not have any snapshots"
