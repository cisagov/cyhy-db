# Standard Python Libraries
from collections.abc import Iterable
import datetime

# Third-Party Libraries
from mongoengine import (
    BooleanField,
    DateTimeField,
    Document,
    IntField,
    ListField,
    ReferenceField,
    StringField,
)

from .ip_address import IPAddressField


class ScanDoc(Document):
    _ip = IPAddressField(db_field="ip", required=True)
    ip_int = IntField(required=True)
    latest = BooleanField(default=True)
    owner = StringField(required=True)
    snapshots = ListField(ReferenceField("SnapshotDoc"))
    source = StringField(required=True)
    time = DateTimeField(default=datetime.datetime.utcnow, required=True)

    meta = {
        "indexes": [
            {"fields": ["latest", "ip_int"], "unique": False},
            {"fields": ["time", "owner"], "unique": False},
            {"fields": ["ip_int"], "unique": False},
            {"fields": ["snapshots"], "unique": False, "sparse": True},
        ]
    }

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, new_ip):
        self._ip = new_ip
        # Convert IP to an integer and store in ip_int
        try:
            self.ip_int = int(self._ip)
        except ValueError:
            raise ValueError(f"Invalid IP address: {new_ip}")

    # Custom methods
    def reset_latest_flag_by_owner(self, owner):
        ScanDoc.objects(latest=True, owner=owner).update(latest=False)

    def reset_latest_flag_by_ip(self, ips):
        ip_ints = [int(x) for x in ips] if isinstance(ips, Iterable) else [int(ips)]
        ScanDoc.objects(latest=True, ip_int__in=ip_ints).update(latest=False)

    def tag_latest(self, owners, snapshot_oid):
        ScanDoc.objects(latest=True, owner__in=owners).update(
            push__snapshots=snapshot_oid
        )

    def tag_matching(self, existing_snapshot_oids, new_snapshot_oid):
        ScanDoc.objects(snapshots__in=existing_snapshot_oids).update(
            push__snapshots=new_snapshot_oid
        )

    def tag_timespan(self, owner, snapshot_oid, start_time, end_time):
        ScanDoc.objects(time__gte=start_time, time__lte=end_time, owner=owner).update(
            push__snapshots=snapshot_oid
        )

    def remove_tag(self, snapshot_oid):
        ScanDoc.objects(snapshots=snapshot_oid).update(pull__snapshots=snapshot_oid)
