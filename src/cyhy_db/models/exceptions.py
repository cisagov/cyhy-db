"""The exceptions used in CyHy."""


class PortScanNotFoundException(Exception):
    """Exception raised when a referenced PortScanDoc is not found."""

    def __init__(self, ticket_id, port_scan_id, port_scan_time, *args):
        """Initialize the exception with the given ticket ID, port scan ID, and port scan time.

        Args:
            ticket_id (str): The ID of the ticket.
            port_scan_id (str): The ID of the port scan.
            port_scan_time (datetime): The time of the port scan.
            *args: Additional arguments to pass to the base Exception class.
        """
        message = "Ticket {}: referenced PortScanDoc {} at time {} not found".format(
            ticket_id, port_scan_id, port_scan_time
        )
        self.ticket_id = ticket_id
        self.port_scan_id = port_scan_id
        self.port_scan_time = port_scan_time
        super().__init__(message, *args)


class VulnScanNotFoundException(Exception):
    """Exception raised when a referenced VulnScanDoc is not found."""

    def __init__(self, ticket_id, vuln_scan_id, vuln_scan_time, *args):
        """Initialize the exception with the given ticket ID, vulnerability scan ID, and vulnerability scan time.

        Args:
            ticket_id (str): The ID of the ticket.
            vuln_scan_id (str): The ID of the vulnerability scan document.
            vuln_scan_time (str): The time of the vulnerability scan.
            *args: Additional arguments to pass to the base exception class.
        """
        message = "Ticket {}: referenced VulnScanDoc {} at time {} not found".format(
            ticket_id, vuln_scan_id, vuln_scan_time
        )
        self.ticket_id = ticket_id
        self.vuln_scan_id = vuln_scan_id
        self.vuln_scan_time = vuln_scan_time
        super().__init__(message, *args)
