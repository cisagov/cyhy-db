"""Regression coverage for raw host input validation."""

# Standard Python Libraries
from ipaddress import IPv4Address

# Third-Party Libraries
from pydantic import ValidationError
import pytest

# cisagov Libraries
from cyhy_db.models import HostDoc


@pytest.mark.parametrize(
    "data", [None, [], "not a mapping", 42, {}, {"owner": "EXAMPLE"}]
)
def test_invalid_model_input_raises_validation_error(data):
    """Malformed input must not escape as a KeyError or TypeError."""
    with pytest.raises(ValidationError):
        HostDoc.model_validate(data)


def test_missing_ip_in_constructor_is_a_field_error():
    """A missing required IP uses the same error contract as other fields."""
    with pytest.raises(ValidationError) as error:
        HostDoc(owner="EXAMPLE")
    assert any(item["loc"] == ("ip",) for item in error.value.errors())


def test_missing_ip_in_json_is_a_field_error():
    """JSON validation also reports a missing IP rather than a raw KeyError."""
    with pytest.raises(ValidationError) as error:
        HostDoc.model_validate_json('{"owner": "EXAMPLE"}')
    assert any(item["loc"] == ("ip",) for item in error.value.errors())


@pytest.mark.parametrize("address", ["not-an-ip", None, "2001:db8::1"])
def test_invalid_addresses_remain_rejected(address):
    """The raw-input guard must not bypass IPv4 field validation."""
    with pytest.raises(ValidationError):
        HostDoc(ip=address, owner="EXAMPLE")


@pytest.mark.parametrize(
    "address",
    ["192.0.2.1", IPv4Address("192.0.2.1"), 3221225985, b"\xc0\x00\x02\x01"],
)
def test_valid_ipv4_inputs_keep_integer_ids(address):
    """Keep deriving the same ID from every supported IPv4 representation."""
    host = HostDoc(ip=address, owner="EXAMPLE")
    assert host.ip == IPv4Address("192.0.2.1")
    assert host.id == 3221225985


def test_existing_model_can_be_validated_again():
    """Validation of an existing host must retain its calculated ID."""
    host = HostDoc(ip="192.0.2.1", owner="EXAMPLE")
    result = HostDoc.model_validate(host)
    assert result.ip == host.ip
    assert result.id == host.id
