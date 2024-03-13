# Standard Python Libraries
from ipaddress import ip_address

# cisagov Libraries
from cyhy_db.models import HostDoc

VALID_IP_1_STR = "0.0.0.1"
VALID_IP_2_STR = "0.0.0.2"
VALID_IP_1_INT = int(ip_address(VALID_IP_1_STR))
VALID_IP_2_INT = int(ip_address(VALID_IP_2_STR))


def test_host_doc_init():
    # Create a HostDoc object
    host_doc = HostDoc(
        ip=ip_address(VALID_IP_1_STR),
        owner="YOUR_MOM",
    )


async def test_save():
    # Create a HostDoc object
    host_doc = HostDoc(
        ip=ip_address(VALID_IP_1_STR),
        owner="YOUR_MOM",
    )
    # Save the HostDoc object to the database
    await host_doc.save()
    assert host_doc.id == VALID_IP_1_INT


async def test_get_by_ip():
    # Find a HostDoc object by its IP address
    host_doc = await HostDoc.get_by_ip(ip_address(VALID_IP_1_STR))
    assert host_doc.ip == ip_address(VALID_IP_1_STR)
