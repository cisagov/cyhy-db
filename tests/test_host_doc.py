"""Test HostDoc model functionality."""

# Standard Python Libraries
from ipaddress import ip_address

# cisagov Libraries
from cyhy_db.models import HostDoc

VALID_IP_1_STR = "0.0.0.1"
VALID_IP_2_STR = "0.0.0.2"
VALID_IP_1_INT = int(ip_address(VALID_IP_1_STR))
VALID_IP_2_INT = int(ip_address(VALID_IP_2_STR))


def test_host_doc_init():
    """Test HostDoc object initialization."""
    # Create a HostDoc object
    host_doc = HostDoc(
        ip=ip_address(VALID_IP_1_STR),
        owner="YOUR_MOM",
    )
    # Check that the HostDoc object was created correctly
    assert host_doc.ip == ip_address(VALID_IP_1_STR)


async def test_save():
    """Test saving a HostDoc object to the database."""
    # Create a HostDoc object
    host_doc = HostDoc(
        ip=ip_address(VALID_IP_1_STR),
        owner="YOUR_MOM",
    )
    # Save the HostDoc object to the database
    await host_doc.save()
    assert host_doc.id == VALID_IP_1_INT


async def test_get_by_ip():
    """Test finding a HostDoc object by its IP address."""
    # Find a HostDoc object by its IP address
    host_doc = await HostDoc.get_by_ip(ip_address(VALID_IP_1_STR))
    assert host_doc.ip == ip_address(VALID_IP_1_STR)
