"""The enumerations used in CyHy."""

# Standard Python Libraries
from enum import StrEnum, auto


class AgencyType(StrEnum):
    """Agency types."""

    FEDERAL = auto()
    LOCAL = auto()
    PRIVATE = auto()
    STATE = auto()
    TERRITORIAL = auto()
    TRIBAL = auto()


class ControlAction(StrEnum):
    """Commander control actions."""

    PAUSE = auto()
    STOP = auto()


class ControlTarget(StrEnum):
    """Commander control targets."""

    COMMANDER = auto()


class CVSSVersion(StrEnum):
    """CVSS versions."""

    V2 = auto()
    V3 = auto()
    V3_1 = auto()


class DayOfWeek(StrEnum):
    """Days of the week."""

    MONDAY = auto()
    TUESDAY = auto()
    WEDNESDAY = auto()
    THURSDAY = auto()
    FRIDAY = auto()
    SATURDAY = auto()
    SUNDAY = auto()


class PocType(StrEnum):
    """Point of contact types."""

    DISTRO = auto()
    TECHNICAL = auto()


class Protocol(StrEnum):
    """Network protocols."""

    TCP = auto()
    UDP = auto()


class ReportPeriod(StrEnum):
    """CyHy reporting periods."""

    MONTHLY = auto()
    QUARTERLY = auto()
    WEEKLY = auto()


class ReportType(StrEnum):
    """CyHy report types."""

    BOD = auto()
    CYBEX = auto()
    CYHY = auto()
    CYHY_THIRD_PARTY = auto()
    DNSSEC = auto()
    PHISHING = auto()


class ScanType(StrEnum):
    """CyHy scan types."""

    CYHY = auto()
    DNSSEC = auto()
    PHISHING = auto()


class Scheduler(StrEnum):
    """CyHy schedulers."""

    PERSISTENT1 = auto()


class Stage(StrEnum):
    """CyHy scan stages."""

    BASESCAN = auto()  # TODO: Delete if unused
    NETSCAN1 = auto()
    NETSCAN2 = auto()
    PORTSCAN = auto()
    VULNSCAN = auto()


class Status(StrEnum):
    """CyHy scan statuses."""

    DONE = auto()
    READY = auto()
    RUNNING = auto()
    WAITING = auto()


class TicketAction(StrEnum):
    """Actions for ticket events."""

    CHANGED = auto()
    CLOSED = auto()
    OPENED = auto()
    REOPENED = auto()
    UNVERIFIED = auto()
    VERIFIED = auto()
