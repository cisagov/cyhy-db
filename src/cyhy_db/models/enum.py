"""The enumerations used in CyHy."""

# Standard Python Libraries
from enum import Enum


class AgencyType(Enum):
    """Agency types."""

    FEDERAL = "FEDERAL"
    LOCAL = "LOCAL"
    PRIVATE = "PRIVATE"
    STATE = "STATE"
    TERRITORIAL = "TERRITORIAL"
    TRIBAL = "TRIBAL"


class ControlAction(Enum):
    """Commander control actions."""

    PAUSE = "PAUSE"
    STOP = "STOP"


class ControlTarget(Enum):
    """Commander control targets."""

    COMMANDER = "COMMANDER"


class CVSSVersion(Enum):
    """CVSS versions."""

    V2 = "2.0"
    V3 = "3.0"
    V3_1 = "3.1"


class DayOfWeek(Enum):
    """Days of the week."""

    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class PocType(Enum):
    """Point of contact types."""

    DISTRO = "DISTRO"
    TECHNICAL = "TECHNICAL"


class Protocol(Enum):
    """Protocols."""

    TCP = "tcp"
    UDP = "udp"


class ReportPeriod(Enum):
    """CyHy reporting periods."""

    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    WEEKLY = "WEEKLY"


class ReportType(Enum):
    """CyHy report types."""

    BOD = "BOD"
    CYBEX = "CYBEX"
    CYHY = "CYHY"
    CYHY_THIRD_PARTY = "CYHY_THIRD_PARTY"
    DNSSEC = "DNSSEC"
    PHISHING = "PHISHING"


class ScanType(Enum):
    """CyHy scan types."""

    CYHY = "CYHY"
    DNSSEC = "DNSSEC"
    PHISHING = "PHISHING"


class Scheduler(Enum):
    """CyHy schedulers."""

    PERSISTENT1 = "PERSISTENT1"


class Stage(Enum):
    """CyHy scan stages."""

    BASESCAN = "BASESCAN"  # TODO: Delete if unused
    NETSCAN1 = "NETSCAN1"
    NETSCAN2 = "NETSCAN2"
    PORTSCAN = "PORTSCAN"
    VULNSCAN = "VULNSCAN"


class Status(Enum):
    """CyHy scan statuses."""

    DONE = "DONE"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"


class TicketEvent(Enum):
    """Ticket events."""

    CHANGED = "CHANGED"
    CLOSED = "CLOSED"
    OPENED = "OPENED"
    REOPENED = "REOPENED"
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
