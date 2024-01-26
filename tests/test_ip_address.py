# Standard Python Libraries
import ipaddress

# Third-Party Libraries
from mongoengine import Document, ValidationError
import pytest

# cisagov Libraries
from cyhy_db.models.ip_address import IPAddressField


class HasIpDocument(Document):
    ip = IPAddressField()


def test_ip_address_type():
    doc = HasIpDocument(ip="1.2.3.4")
    assert isinstance(doc.ip, (ipaddress.IPv4Address, ipaddress.IPv6Address))


@pytest.mark.parametrize(
    "valid_ip",
    [
        "192.168.1.1",
        "10.0.0.1",
        "255.255.255.255",
    ],
)
def test_valid_ip_address_field(valid_ip):
    try:
        HasIpDocument(ip=valid_ip).validate()
    except ValidationError:
        pytest.fail(f"Valid IP address {valid_ip} raised ValidationError")


@pytest.mark.parametrize(
    "invalid_ip",
    [
        "256.256.256.256",
        "123.456.789.0",
        "abc.def.ghi.jkl",
    ],
)
def test_invalid_ip_address_field(invalid_ip):
    with pytest.raises(ValidationError):
        HasIpDocument(ip=invalid_ip).validate()


def test_save_ip_address(mongodb_engine):
    test_document = HasIpDocument(ip=ipaddress.IPv4Address("192.168.1.1"))
    test_document.save()
    assert test_document.id is not None, "TestDocument instance was not saved correctly"


def test_retrieve_ip_address(mongodb_engine):
    retrieved_doc = HasIpDocument.objects().first()
    assert retrieved_doc is not None, "TestDocument instance was not retrieved"
    assert retrieved_doc.ip == ipaddress.IPv4Address(
        "192.168.1.1"
    ), "Retrieved IP address does not match the saved IP address"
