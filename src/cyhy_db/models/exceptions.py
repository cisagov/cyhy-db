"""The exceptions used in CyHy."""


class PortScanNotFoundError(Exception):
    """Exception raised when a referenced PortScanDoc is not found."""

    def __init__(self, ticket_id, port_scan_id, port_scan_time, *args):
        """Initialize with the given ticket ID, port scan ID, and port scan time.

        Args:
            ticket_id (str): The ID of the ticket.
            port_scan_id (str): The ID of the port scan.
            port_scan_time (datetime): The time of the port scan.
            *args: Additional arguments to pass to the base Exception class.
        """
        self.ticket_id = ticket_id
        self.port_scan_id = port_scan_id
        self.port_scan_time = port_scan_time
        super().__init__(ticket_id, port_scan_id, port_scan_time, *args)

    def __str__(self):
        """Return a human-readable description of the exception."""
        return (
            f"Ticket {self.ticket_id}: referenced PortScanDoc {self.port_scan_id} "
            f"at time {self.port_scan_time} not found"
        )


class VulnScanNotFoundError(Exception):
    """Exception raised when a referenced VulnScanDoc is not found."""

    def __init__(self, ticket_id, vuln_scan_id, vuln_scan_time, *args):
        """Initialize with the given ticket ID, vuln scan ID, and vuln scan time.

        Args:
            ticket_id (str): The ID of the ticket.
            vuln_scan_id (str): The ID of the vulnerability scan document.
            vuln_scan_time (str): The time of the vulnerability scan.
            *args: Additional arguments to pass to the base exception class.
        """
        self.ticket_id = ticket_id
        self.vuln_scan_id = vuln_scan_id
        self.vuln_scan_time = vuln_scan_time
        super().__init__(ticket_id, vuln_scan_id, vuln_scan_time, *args)

    def __str__(self):
        """Return a human-readable description of the exception."""
        return (
            f"Ticket {self.ticket_id}: referenced VulnScanDoc {self.vuln_scan_id} "
            f"at time {self.vuln_scan_time} not found"
        )
