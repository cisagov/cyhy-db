# Scan documents (order matters)
from .scan_doc import ScanDoc
from .host_scan_doc import HostScanDoc
from .port_scan_doc import PortScanDoc
from .vuln_scan_doc import VulnScanDoc

# Snapshot documents (order matters)
from .snapshot_doc import SnapshotDoc
from .report_doc import ReportDoc

# Other documents
from .cve import CVE
from .host_doc import HostDoc
from .kev_doc import KEVDoc
from .place_doc import PlaceDoc
from .request_doc import RequestDoc
from .system_control_doc import SystemControlDoc
from .tally_doc import TallyDoc


__all__ = [
    "CVE",
    "HostDoc",
    "HostScanDoc",
    "KEVDoc",
    "PlaceDoc",
    "PortScanDoc",
    "RequestDoc",
    "ReportDoc",
    "ScanDoc",
    "SnapshotDoc",
    "SystemControlDoc",
    "TallyDoc",
    "VulnScanDoc",
]
