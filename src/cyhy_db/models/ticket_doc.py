"""The model for CyHy ticket documents."""

# Standard Python Libraries
from datetime import datetime, timedelta
from ipaddress import IPv4Address
from typing import List, Optional, Tuple

# Third-Party Libraries
from beanie import (
    BeanieObjectId,
    Document,
    Insert,
    Link,
    Replace,
    ValidateOnSave,
    before_event,
)
from beanie.operators import In, Pull, Push
from pydantic import BaseModel, ConfigDict, Field
from pymongo import ASCENDING, IndexModel

# cisagov Libraries
from cyhy_db.utils.time import utcnow

from . import PortScanDoc, SnapshotDoc, VulnScanDoc
from .enum import Protocol, TicketAction
from .exceptions import PortScanNotFoundException, VulnScanNotFoundException


class EventDelta(BaseModel):
    """The event delta model."""

    from_: Optional[bool | float | int | str] = Field(..., alias="from")
    key: str = Field(...)
    to: Optional[bool | float | int | str] = Field(...)


class TicketEvent(BaseModel):
    """The ticket event model."""

    action: TicketAction
    delta: Optional[EventDelta] = Field(default_factory=EventDelta())
    reason: str = Field(...)
    reference: BeanieObjectId = Field(...)
    time: datetime


class TicketDoc(Document):
    """The ticket document model."""

    model_config = ConfigDict(extra="forbid")

    details: dict = Field(default_factory=dict)
    events: list[TicketEvent] = Field(default_factory=list)
    false_positive: bool = Field(default=False)
    fp_expiration_date: Optional[datetime] = Field(default=None)
    ip_int: int = Field(...)
    ip: IPv4Address = Field(...)
    last_change: datetime = Field(default_factory=utcnow)
    loc: Optional[Tuple[float, float]] = Field(default=None)
    open: bool = Field(default=True)
    owner: str = Field(...)
    port: int = Field(...)
    protocol: Protocol = Field(...)
    snapshots: Optional[List[Link[SnapshotDoc]]] = Field(default_factory=list)
    source_id: int = Field(...)
    source: str = Field(...)
    time_closed: Optional[datetime] = Field(default=None)
    time_opened: datetime = Field(default_factory=utcnow)

    class Settings:
        """Beanie settings."""

        name = "tickets"

        indexes = [
            IndexModel(
                [
                    ("ip_int", ASCENDING),
                    ("port", ASCENDING),
                    ("protocol", ASCENDING),
                    ("source", ASCENDING),
                    ("source_id", ASCENDING),
                    ("open", ASCENDING),
                    ("false_positive", ASCENDING),
                ],
                name="ip_port_protocol_source_open_false_positive",
            ),
            IndexModel(
                [("ip_int", ASCENDING), ("open", ASCENDING)],
                name="ip_open",
            ),
            IndexModel(
                [("open", ASCENDING), ("owner", ASCENDING)],
                name="open_owner",
            ),
            IndexModel(
                [("time_opened", ASCENDING), ("open", ASCENDING)],
                name="time_opened",
            ),
            IndexModel(
                [("last_change", ASCENDING)],
                name="last_change",
            ),
            IndexModel(
                [("time_closed", ASCENDING)],
                name="time_closed",
                sparse=True,
            ),
        ]

    @before_event(Insert, Replace, ValidateOnSave)
    async def before_save(self):
        """Do a false positive sanity check and set data just prior to saving a ticket document."""
        if self.false_positive and not self.open:
            raise Exception("A ticket marked as a false positive cannot be closed.")
        self.last_change = utcnow()

    def add_event(self, action, reason, reference=None, time=None, delta=None):
        """Add an event to the list of ticket events."""
        if action not in TicketAction:
            raise Exception(
                'Invalid action "' + action + '" cannot be added to ticket events.'
            )
        if not time:
            time = utcnow()
        event = TicketEvent(
            action=action, reason=reason, reference=reference, time=time
        )
        if delta:
            event.delta = delta
        self.events.append(event)

    def false_positive_dates(self):
        """Return most recent false positive effective and expiration dates (if any)."""
        if self.false_positive:
            for event in reversed(self.events):
                if not event.delta:
                    continue
                if (
                    event.action == TicketAction.CHANGED
                    and event.delta.key == "false_positive"
                ):
                    return (event.time, self.fp_expiration_date)
        return None

    def last_detection_date(self):
        """Return date of most recent detection of a ticket's finding."""
        for event in reversed(self.events):
            if event.action in [
                TicketAction.OPENED,
                TicketAction.VERIFIED,
                TicketAction.REOPENED,
            ]:
                return event.time
        # This should never happen, but if we don't find any OPENED/VERIFIED/REOPENED events above, gracefully return time_opened
        return self.time_opened

    async def latest_port(self):
        """Return the last referenced port scan in the event list.

        This should only be used for tickets generated by portscans.
        """
        for event in self.events[::-1]:
            reference_id = event.get("reference")
            if reference_id:
                break
        else:
            raise Exception("No references found in ticket events:", self._id)
        port = await PortScanDoc.get(reference_id)
        if not port:
            # This can occur when a port_scan has been archived
            # Raise an exception with the info we have for this port_scan from the ticket
            raise PortScanNotFoundException(
                ticket_id=self._id,
                port_scan_id=reference_id,
                port_scan_time=event.time,
            )
        return port

    async def latest_vuln(self):
        """Return the last referenced vulnerability in the event list.

        This should only be used for tickets generated by vulnscans.
        """
        for event in self.events[::-1]:
            reference_id = event.get("reference")
            if reference_id:
                break
        else:
            raise Exception("No references found in ticket events:", self._id)
        vuln = await VulnScanDoc.get(reference_id)
        if not vuln:
            # This can occur when a vuln_scan has been archived
            # Raise an exception with the info we have for this vuln_scan from the ticket
            raise VulnScanNotFoundException(
                ticket_id=self._id,
                vuln_scan_id=reference_id,
                vuln_scan_time=event.time,
            )
        return vuln

    def set_false_positive(self, new_state: bool, reason: str, expire_days: int):
        """Mark a ticket as a false positive."""
        if self.false_positive == new_state:
            return

        # Define the event delta
        delta = EventDelta(
            from_=self.false_positive, to=new_state, key="false_positive"
        )

        # Update ticket state
        self.false_positive = new_state
        now = utcnow()
        expiration_date = None

        if new_state:
            # Only include the expiration date when setting false_positive to
            # True
            expiration_date = now + timedelta(days=expire_days)

            # If ticket is not open, re-open it; false positive tix should
            # always be open
            if not self.open:
                self.open = True
                self.time_closed = None
                self.add_event(
                    action=TicketAction.REOPENED,
                    reason="setting false positive",
                    time=now,
                )

        # Add the change event
        self.add_event(
            action=TicketAction.CHANGED, reason=reason, time=now, delta=delta
        )

        # Set ticket expiration date if applicable
        self.fp_expiration_date = expiration_date

    @classmethod
    async def tag_open(cls, owners, snapshot_oid):
        """Add a snapshot object ID to the snapshots field of all open tickets belonging to the specified owners."""
        await cls.find(cls.open is True, In(cls.owner, owners)).update_many(
            Push({cls.snapshots: snapshot_oid})
        )

    @classmethod
    async def tag_matching(cls, existing_snapshot_oids, new_snapshot_oid):
        """Add a new snapshot object ID to the snapshots field of all tickets whose snapshots field contain any of specified existing snapshot object IDs."""
        await cls.find(In(cls.snapshots, existing_snapshot_oids)).update_many(
            Push({cls.snapshots: new_snapshot_oid})
        )

    @classmethod
    async def remove_tag(cls, snapshot_oid):
        """Remove the specified snapshot object ID from the snapshots field of all tickets whose snapshots field contain that snapshot object ID."""
        await cls.find(In(cls.snapshots, snapshot_oid)).update_many(
            Pull({cls.snapshots: snapshot_oid})
        )
