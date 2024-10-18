"""Test HostDoc model functionality."""

# Standard Python Libraries
from ipaddress import ip_address

# cisagov Libraries
from cyhy_db.models import HostDoc
from cyhy_db.models.host_doc import State

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


async def test_set_state_open_ports():
    """Test setting HostDoc state with open ports."""
    # Find a HostDoc object by its IP address
    host_doc = await HostDoc.get_by_ip(ip_address(VALID_IP_1_STR))
    host_doc.set_state(nmap_says_up=None, has_open_ports=True)
    assert host_doc.state == State(up=True, reason="open-port")


async def test_set_state_no_open_ports():
    """Test setting HostDoc state with no open ports."""
    # Find a HostDoc object by its IP address
    host_doc = await HostDoc.get_by_ip(ip_address(VALID_IP_1_STR))
    host_doc.set_state(nmap_says_up=None, has_open_ports=False)
    assert host_doc.state == State(up=False, reason="no-open")


async def test_set_state_nmap_says_down():
    """Test setting HostDoc state when nmap says the host is down."""
    # Find a HostDoc object by its IP address
    host_doc = await HostDoc.get_by_ip(ip_address(VALID_IP_1_STR))
    host_doc.set_state(nmap_says_up=False, has_open_ports=None, reason="no-reply")
    assert host_doc.state == State(up=False, reason="no-reply")


async def test_set_state_no_op():
    """Test setting HostDoc state when inputs are supplied that results in no state change."""
    # Create a HostDoc object
    host_doc = HostDoc(
        ip=ip_address(VALID_IP_2_STR),
        owner="NO-OP",
    )
    # Save the HostDoc object to the database
    await host_doc.save()
    assert host_doc.id == VALID_IP_2_INT

    # Find HostDoc object by its IP address
    host_doc = await HostDoc.get_by_ip(ip_address(VALID_IP_2_INT))
    assert host_doc.state == State(up=False, reason="new")

    host_doc.set_state(nmap_says_up=True, has_open_ports=None, reason="no-op-test-1")
    assert host_doc.state == State(up=False, reason="new")

    host_doc.set_state(nmap_says_up=None, has_open_ports=None, reason="no-op-test-2")
    assert host_doc.state == State(up=False, reason="new")
