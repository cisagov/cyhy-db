"""Test TicketDoc model functionality."""

# Standard Python Libraries
from datetime import timedelta
from ipaddress import IPv4Address
from unittest.mock import AsyncMock, patch

# Third-Party Libraries
from beanie import PydanticObjectId
import pytest

# cisagov Libraries
from cyhy_db.models.enum import Protocol, TicketAction
from cyhy_db.models.exceptions import (
    PortScanNotFoundException,
    VulnScanNotFoundException,
)
from cyhy_db.models.port_scan_doc import PortScanDoc
from cyhy_db.models.snapshot_doc import SnapshotDoc
from cyhy_db.models.ticket_doc import EventDelta, TicketDoc, TicketEvent
from cyhy_db.models.vuln_scan_doc import VulnScanDoc
from cyhy_db.utils.time import utcnow

VALID_IP_1_STR = "0.0.0.1"
VALID_IP_1_INT = int(IPv4Address(VALID_IP_1_STR))


def sample_ticket():
    """Create a sample TicketDoc object."""
    return TicketDoc(
        ip_int=VALID_IP_1_INT,
        ip=IPv4Address(VALID_IP_1_STR),
        owner="TICKET-TEST-1",
        port=80,
        protocol=Protocol.TCP,
        source_id=1,
        source="test",
    )


def test_init():
    """Test TicketDoc object initialization."""
    # Create a TicketDoc object
    ticket_doc = sample_ticket()

    # Verify that default values are set correctly
    assert ticket_doc.details == {}, "details was not set to an empty dict"
    assert ticket_doc.events == [], "events was not set to an empty list"
    assert ticket_doc.false_positive is False, "false_positive was not set to False"
    assert ticket_doc.last_change is not None, "last_change was not set"
    assert ticket_doc.open is True, "open was not set to True"
    assert ticket_doc.snapshots == [], "snapshots was not set to an empty list"
    assert ticket_doc.time_closed is None, "time_closed was not set to None"
    assert ticket_doc.time_opened is not None, "time_opened was not set"


async def test_save():
    """Test saving a TicketDoc object to the database."""
    # Create a TicketDoc object and save it to the DB
    ticket_doc = sample_ticket()
    await ticket_doc.save()

    # Find ticket in DB and confirm it was saved correctly
    ticket_doc_db = await TicketDoc.find_one(TicketDoc.ip_int == VALID_IP_1_INT)
    assert ticket_doc_db is not None, "ticket_doc was not saved to the database"


async def test_save_with_event():
    """Test saving a ticket that contains an event."""
    ticket_doc = await TicketDoc.find_one(TicketDoc.ip_int == VALID_IP_1_INT)
    ticket_doc.set_false_positive(
        new_state=True, reason="Test set false positive", expire_days=30
    )
    await ticket_doc.save()

    # Find ticket in DB and confirm it was saved correctly
    ticket_doc_db = await TicketDoc.find_one(TicketDoc.ip_int == VALID_IP_1_INT)
    assert ticket_doc_db is not None, "ticket_doc was not saved to the database"
    assert ticket_doc_db.events[0].action == TicketAction.CHANGED
    assert ticket_doc_db.events[0].delta.from_ is False
    assert ticket_doc_db.events[0].delta.to is True


async def test_before_save():
    """Test the before_save method."""
    ticket_doc = sample_ticket()
    ticket_doc.false_positive = True
    ticket_doc.open = False
    with pytest.raises(
        Exception, match="A ticket marked as a false positive cannot be closed."
    ):
        await ticket_doc.save()


def test_add_event():
    """Test adding an event to a ticket."""
    ticket_doc = sample_ticket()
    ticket_doc.add_event(action=TicketAction.OPENED, reason="Test reason")
    assert len(ticket_doc.events) == 1, "event was not added to the ticket"
    assert ticket_doc.events[0].action == TicketAction.OPENED
    assert ticket_doc.events[0].reason == "Test reason"


def test_add_event_exception():
    """Test adding an invalid event to a ticket."""
    ticket_doc = sample_ticket()
    with pytest.raises(
        Exception, match='Invalid action "INVALID" cannot be added to ticket events.'
    ):
        ticket_doc.add_event(action="INVALID", reason="Test reason")


def test_set_false_positive_true():
    """Test setting a ticket as false positive."""
    ticket_doc = sample_ticket()
    ticket_doc.set_false_positive(
        new_state=True, reason="Test set false positive", expire_days=30
    )
    assert ticket_doc.false_positive is True, "ticket was not set as false positive"
    assert (
        ticket_doc.fp_expiration_date is not None
    ), "false positive expiration date was not set"


def test_set_false_positive_no_change():
    """Test setting a ticket that was already false positive to false positive."""
    ticket_doc = sample_ticket()

    ticket_doc.set_false_positive(
        new_state=True, reason="Test set false positive", expire_days=30
    )
    fp_expiration_date = ticket_doc.fp_expiration_date

    ticket_doc.set_false_positive(
        new_state=True, reason="Test set false positive again", expire_days=60
    )
    assert (
        ticket_doc.false_positive is True
    ), "ticket should have remained a false positive"
    assert (
        ticket_doc.fp_expiration_date == fp_expiration_date
    ), "false positive expiration date should not have changed"


def test_set_false_positive_false():
    """Test setting a ticket as false positive false."""
    ticket_doc = sample_ticket()
    ticket_doc.set_false_positive(
        new_state=True, reason="Test set false positive true", expire_days=30
    )

    assert (
        ticket_doc.fp_expiration_date is not None
    ), "false positive expiration date was not set"

    ticket_doc.set_false_positive(
        new_state=False, reason="Test set false positive false", expire_days=0
    )
    assert (
        ticket_doc.false_positive is False
    ), "ticket should not still be false positive"
    assert (
        ticket_doc.fp_expiration_date is None
    ), "false positive expiration date was not cleared"


def test_set_false_positive_on_closed_ticket():
    """Test setting a closed ticket as false positive."""
    ticket_doc = sample_ticket()
    # Close the ticket
    ticket_doc.open = False
    ticket_doc.time_closed = utcnow()

    ticket_doc.set_false_positive(
        expire_days=30,
        new_state=True,
        reason="Test set false positive on closed ticket",
    )
    assert ticket_doc.open is True, "ticket should have been reopened"
    assert ticket_doc.false_positive is True, "ticket should be false positive"
    assert ticket_doc.time_closed is None, "ticket should not have a time_closed"
    assert ticket_doc.events[-2].action == TicketAction.REOPENED
    assert ticket_doc.events[-2].reason == "setting false positive"
    assert ticket_doc.events[-2].time is not None


def test_false_positive_dates():
    """Test getting false positive dates."""
    ticket_doc = sample_ticket()

    # Set ticket as false positive
    ticket_doc.set_false_positive(
        new_state=True, reason="Test set false positive", expire_days=30
    )
    fp_dates = ticket_doc.false_positive_dates()
    assert fp_dates is not None

    # Add another sample event
    ticket_doc.add_event(
        action=TicketAction.UNVERIFIED, reason="Test reason", time=utcnow()
    )
    assert ticket_doc.false_positive_dates() == fp_dates

    # Unset ticket as false positive
    ticket_doc.false_positive = False
    event = TicketEvent(
        action=TicketAction.CHANGED,
        delta=EventDelta(from_=True, to=False, key="false_positive"),
        reason="Test false positive expired",
        reference=None,
        time=utcnow(),
    )
    ticket_doc.events.append(event)
    assert ticket_doc.false_positive_dates() is None


def test_false_positive_dates_edge_cases():
    """Test getting false positive dates edge cases."""
    ticket_doc = sample_ticket()
    ticket_doc.false_positive = True
    assert ticket_doc.false_positive_dates() is None

    # Add a sample non-false-positive CHANGED event
    test_delta = EventDelta(from_=False, to=True, key="test_key")
    ticket_doc.add_event(
        action=TicketAction.CHANGED,
        delta=test_delta,
        reason="Test reason",
        time=utcnow(),
    )
    assert ticket_doc.false_positive_dates() is None


def test_last_detection_date():
    """Test getting the last detection date."""
    ticket_doc = sample_ticket()
    ticket_doc.add_event(
        action=TicketAction.OPENED, reason="Test reason", time=utcnow()
    )
    detection_date = ticket_doc.last_detection_date()
    assert detection_date == ticket_doc.events[0].time


def test_last_detection_date_edge_case():
    """Test an edge case of last_detection_date."""
    ticket_doc = sample_ticket()
    ticket_doc.add_event(
        action=TicketAction.CLOSED, reason="Test reason", time=utcnow()
    )
    detection_date = ticket_doc.last_detection_date()
    assert detection_date == ticket_doc.time_opened


async def test_tagging():
    """Test tag_open, tag_matching, and remove_tag."""
    # Find our test ticket in the DB
    ticket_doc_db = await TicketDoc.find_one(TicketDoc.ip_int == VALID_IP_1_INT)
    test_owner = ticket_doc_db.owner
    assert len(ticket_doc_db.snapshots) == 0

    # Create a test snapshot and save it to the DB
    snapshot_end_time = utcnow()
    snapshot_start_time = snapshot_end_time - timedelta(days=1)
    test_snapshot_1 = SnapshotDoc(
        owner=test_owner, end_time=snapshot_end_time, start_time=snapshot_start_time
    )
    await test_snapshot_1.save()
    assert test_snapshot_1 not in ticket_doc_db.snapshots

    # Use tag_open() to tag the ticket with the snapshot ID
    await TicketDoc.tag_open(owners=[test_owner], snapshot_oid=test_snapshot_1.id)

    updated_ticket = await TicketDoc.find_one(TicketDoc.ip_int == VALID_IP_1_INT)
    # I'm not using fetch_links=True in the find_one() above because I can't get
    # it to work correctly.  Instead, I'm using fetch_all_links() below.
    await updated_ticket.fetch_all_links()
    assert len(updated_ticket.snapshots) == 1
    assert test_snapshot_1 in updated_ticket.snapshots

    # Create another test snapshot and save it to the DB
    snapshot_end_time = utcnow()
    snapshot_start_time = snapshot_end_time - timedelta(days=1)
    test_snapshot_2 = SnapshotDoc(
        owner=test_owner, end_time=snapshot_end_time, start_time=snapshot_start_time
    )
    await test_snapshot_2.save()
    assert test_snapshot_2 not in updated_ticket.snapshots

    # Use tag_matching() to tag the ticket with the new snapshot ID
    await TicketDoc.tag_matching(
        existing_snapshot_oids=[test_snapshot_1.id],
        new_snapshot_oid=test_snapshot_2.id,
    )

    updated_ticket = await TicketDoc.find_one(TicketDoc.ip_int == VALID_IP_1_INT)
    # I'm not using fetch_links=True in the find_one() above because I can't get
    # it to work correctly.  Instead, I'm using fetch_all_links() below.
    await updated_ticket.fetch_all_links()
    assert len(updated_ticket.snapshots) == 2
    assert test_snapshot_2 in updated_ticket.snapshots

    # Use remove_tag() to remove the test_snapshot_2.id from the ticket
    await TicketDoc.remove_tag(snapshot_oid=test_snapshot_2.id)

    updated_ticket = await TicketDoc.find_one(TicketDoc.ip_int == VALID_IP_1_INT)
    # I'm not using fetch_links=True in the find_one() above because I can't get
    # it to work correctly.  Instead, I'm using fetch_all_links() below.
    await updated_ticket.fetch_all_links()
    assert len(updated_ticket.snapshots) == 1
    assert test_snapshot_2 not in updated_ticket.snapshots


async def test_latest_port():
    """Test the latest_port method."""
    ticket_doc = sample_ticket()
    ticket_doc.id = PydanticObjectId()
    reference_id = PydanticObjectId()
    # Add an event with our test reference ID
    ticket_doc.add_event(
        action=TicketAction.OPENED,
        reason="Test reason",
        reference=reference_id,
        time=utcnow(),
    )
    # Add another event without a reference ID
    ticket_doc.add_event(
        action=TicketAction.VERIFIED,
        reason="Test reason",
        time=utcnow(),
    )

    # Create a dummy port scan document with the reference ID
    mock_doc = AsyncMock()
    mock_doc.id = reference_id

    with patch.object(PortScanDoc, "get", return_value=mock_doc):
        port = await ticket_doc.latest_port()
        assert (
            port.id == reference_id
        ), "latest_port did not return the correct port scan"


async def test_latest_port_no_references():
    """Test the latest_port method when there are no references."""
    ticket_doc = sample_ticket()
    ticket_doc.id = PydanticObjectId()

    with pytest.raises(
        Exception, match=("No references found in ticket events: " + str(ticket_doc.id))
    ):
        await ticket_doc.latest_port()


async def test_latest_port_not_found():
    """Test the latest_port method when the port scan is not found."""
    ticket_doc = sample_ticket()
    reference_id = PydanticObjectId()
    ticket_doc.add_event(
        action=TicketAction.OPENED,
        reason="Test reason",
        reference=reference_id,
        time=utcnow(),
    )

    with pytest.raises(PortScanNotFoundException):
        # Mock PortScanDoc.get to return None
        with patch.object(PortScanDoc, "get", return_value=None):
            await ticket_doc.latest_port()


async def test_latest_vuln():
    """Test the latest_vuln method."""
    ticket_doc = sample_ticket()
    reference_id = PydanticObjectId()
    # Add an event with our test reference ID
    ticket_doc.add_event(
        action=TicketAction.OPENED,
        reason="Test reason",
        reference=reference_id,
        time=utcnow(),
    )
    # Add another event without a reference ID
    ticket_doc.add_event(
        action=TicketAction.VERIFIED,
        reason="Test reason",
        time=utcnow(),
    )

    # Create a dummy port scan document with the reference ID
    mock_doc = AsyncMock()
    mock_doc._id = reference_id

    with patch.object(VulnScanDoc, "get", return_value=mock_doc):
        vuln = await ticket_doc.latest_vuln()
        assert (
            vuln._id == reference_id
        ), "latest_vuln did not return the correct vuln scan"


async def test_latest_vuln_no_references():
    """Test the latest_vuln method when there are no references."""
    ticket_doc = sample_ticket()
    ticket_doc.id = PydanticObjectId()

    with pytest.raises(
        Exception, match=("No references found in ticket events: " + str(ticket_doc.id))
    ):
        await ticket_doc.latest_vuln()


async def test_latest_vuln_not_found():
    """Test the latest_vuln method when the port scan is not found."""
    ticket_doc = sample_ticket()
    reference_id = PydanticObjectId()
    ticket_doc.add_event(
        action=TicketAction.OPENED,
        reason="Test reason",
        reference=reference_id,
        time=utcnow(),
    )

    with pytest.raises(VulnScanNotFoundException):
        # Mock VulnScanDoc.get to return None
        with patch.object(VulnScanDoc, "get", return_value=None):
            await ticket_doc.latest_vuln()
