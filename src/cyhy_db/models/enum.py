# Standard Python Libraries
from enum import Enum


class AgencyType(Enum):
    FEDERAL = "FEDERAL"
    LOCAL = "LOCAL"
    PRIVATE = "PRIVATE"
    STATE = "STATE"
    TERRITORIAL = "TERRITORIAL"
    TRIBAL = "TRIBAL"


class ControlAction(Enum):
    PAUSE = "PAUSE"
    STOP = "STOP"


class ControlTarget(Enum):
    COMMANDER = "COMMANDER"


class CVSSVersion(Enum):
    V2 = "2.0"
    V3 = "3.0"
    V3_1 = "3.1"


class DayOfWeek(Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class PocType(Enum):
    DISTRO = "DISTRO"
    TECHNICAL = "TECHNICAL"


class ReportPeriod(Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    WEEKLY = "WEEKLY"


class ReportType(Enum):
    BOD = "BOD"
    CYBEX = "CYBEX"
    CYHY = "CYHY"
    CYHY_THIRD_PARTY = "CYHY_THIRD_PARTY"
    DNSSEC = "DNSSEC"
    PHISHING = "PHISHING"


class ScanType(Enum):
    CYHY = "CYHY"
    DNSSEC = "DNSSEC"
    PHISHING = "PHISHING"


class Scheduler(Enum):
    PERSISTENT1 = "PERSISTENT1"


class Stage(Enum):
    BASESCAN = "BASESCAN"
    NETSCAN1 = "NETSCAN1"
    NETSCAN2 = "NETSCAN2"
    PORTSCAN = "PORTSCAN"
    VULNSCAN = "VULNSCAN"


class Status(Enum):
    DONE = "DONE"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"


class TicketEvent(Enum):
    CHANGED = "CHANGED"
    CLOSED = "CLOSED"
    OPENED = "OPENED"
    REOPENED = "REOPENED"
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
