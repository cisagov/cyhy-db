"""
This module generates test data for CyHy reports using factory classes.

It includes factories for creating instances of various models such as CVE,
Agency, Contact, Location, Window, and RequestDoc. Additionally, it provides a
custom provider for generating specific data like CVE IDs and IPv4 networks.
"""

# Standard Python Libraries
from datetime import datetime
import ipaddress
import random

# Third-Party Libraries
import factory
from mimesis import Generic
from mimesis.locales import DEFAULT_LOCALE
from mimesis.providers.base import BaseProvider
from pytest_factoryboy import register

# cisagov Libraries
from cyhy_db.models import CVEDoc, RequestDoc
from cyhy_db.models.enum import (
    AgencyType,
    CVSSVersion,
    DayOfWeek,
    PocType,
    ReportPeriod,
    ScanType,
    Scheduler,
    Stage,
)
from cyhy_db.models.request_doc import Agency, Contact, Location, Window
from cyhy_db.utils import utcnow


class CyHyProvider(BaseProvider):
    """Custom provider for generating specific CyHy data."""

    class Meta:
        """Meta class for CyHyProvider."""

        name = "cyhy_provider"

    def cve_id(self, year=None):
        """
        Generate a CVE ID.

        Args:
            year (int, optional): The year for the CVE ID. If None, a random
            year between 1999 and the current year is used.

        Returns:
            str: A CVE ID in the format CVE-YYYY-NNNNN.
        """
        if year is None:
            year = self.random.randint(1999, datetime.now().year)
        number = self.random.randint(1, 99999)
        return f"CVE-{year}-{number:05d}"

    def network_ipv4(self):
        """
        Generate an IPv4 network.

        Returns:
            ipaddress.IPv4Network: A randomly generated IPv4 network.
        """
        base_ip = generic.internet.ip_v4()
        # The following line generates a warning from bandit about "Standard
        # pseudo-random generators are not suitable for security/cryptographic
        # purposes."  We aren't using Random() for the purposes of cryptography
        # here, so we can safely ignore that warning.
        cidr = random.randint(24, 30)  # nosec B311
        network = ipaddress.IPv4Network(f"{base_ip}/{cidr}", strict=False)
        return network


generic = Generic(locale=DEFAULT_LOCALE)
generic.add_provider(CyHyProvider)


@register
class CVEFactory(factory.Factory):
    """Factory for creating CVE instances."""

    class Meta:
        """Meta class for CVEFactory."""

        model = CVEDoc

    id = factory.LazyFunction(lambda: generic.cyhy_provider.cve_id())
    # The following lines generate warnings from bandit about "Standard
    # pseudo-random generators are not suitable for security/cryptographic
    # purposes."  We aren't using Random() for the purposes of cryptography
    # here, so we can safely ignore those warnings.
    cvss_score = factory.LazyFunction(
        lambda: round(random.uniform(0, 10), 1)  # nosec B311
    )
    cvss_version = factory.LazyFunction(
        lambda: random.choice(list(CVSSVersion))  # nosec B311
    )
    severity = factory.LazyFunction(lambda: random.randint(1, 4))  # nosec B311


class AgencyFactory(factory.Factory):
    """Factory for creating Agency instances."""

    class Meta:
        """Meta class for AgencyFactory."""

        model = Agency

    name = factory.Faker("company")
    acronym = factory.LazyAttribute(
        lambda o: "".join(word[0].upper() for word in o.name.split())
    )
    # The following lines generate warnings from bandit about "Standard
    # pseudo-random generators are not suitable for security/cryptographic
    # purposes."  We aren't using Random() for the purposes of cryptography
    # here, so we can safely ignore those warnings.
    type = factory.LazyFunction(lambda: random.choice(list(AgencyType)))  # nosec B311
    contacts = factory.LazyFunction(
        lambda: [ContactFactory() for _ in range(random.randint(1, 5))]  # nosec B311
    )
    location = factory.LazyFunction(lambda: LocationFactory())


class ContactFactory(factory.Factory):
    """Factory for creating Contact instances."""

    class Meta:
        """Meta class for ContactFactory."""

        model = Contact

    email = factory.Faker("email")
    name = factory.Faker("name")
    phone = factory.Faker("phone_number")
    # The following line generates a warning from bandit about "Standard
    # pseudo-random generators are not suitable for security/cryptographic
    # purposes."  We aren't using Random() for the purposes of cryptography
    # here, so we can safely ignore that warning.
    type = factory.LazyFunction(lambda: random.choice(list(PocType)))  # nosec B311


class LocationFactory(factory.Factory):
    """Factory for creating Location instances."""

    class Meta:
        """Meta class for LocationFactory."""

        model = Location

    country_name = factory.Faker("country")
    country = factory.Faker("country_code")
    county_fips = factory.Faker("numerify", text="##")
    county = factory.Faker("city")
    gnis_id = factory.Faker("numerify", text="#######")
    name = factory.Faker("city")
    state_fips = factory.Faker("numerify", text="##")
    state_name = factory.Faker("state")
    state = factory.Faker("state_abbr")


class WindowFactory(factory.Factory):
    """Factory for creating Window instances."""

    class Meta:
        """Meta class for WindowFactory."""

        model = Window

    # The following lines generate warnings from bandit about "Standard
    # pseudo-random generators are not suitable for security/cryptographic
    # purposes."  We aren't using Random() for the purposes of cryptography
    # here, so we can safely ignore those warnings.
    day = factory.LazyFunction(lambda: random.choice(list(DayOfWeek)))  # nosec B311
    duration = factory.LazyFunction(lambda: random.randint(0, 168))  # nosec B311
    start = factory.Faker("time", pattern="%H:%M:%S")


class RequestDocFactory(factory.Factory):
    """Factory for creating RequestDoc instances."""

    class Meta:
        """Meta class for RequestDocFactory."""

        model = RequestDoc

    # The following lines generate warnings from bandit about "Standard
    # pseudo-random generators are not suitable for security/cryptographic
    # purposes."  We aren't using Random() for the purposes of cryptography
    # here, so we can safely ignore those warnings.
    id = factory.LazyAttribute(
        lambda o: o.agency.acronym + "-" + str(random.randint(1, 1000))  # nosec B311
    )
    agency = factory.SubFactory(AgencyFactory)
    enrolled = factory.LazyFunction(utcnow)
    init_stage = factory.LazyFunction(lambda: random.choice(list(Stage)))  # nosec B311
    key = factory.Faker("password")
    period_start = factory.LazyFunction(utcnow)
    report_period = factory.LazyFunction(
        lambda: random.choice(list(ReportPeriod))  # nosec B311
    )
    retired = factory.LazyFunction(lambda: random.choice([True, False]))  # nosec B311
    scheduler = factory.LazyFunction(
        lambda: random.choice(list(Scheduler))  # nosec B311
    )
    stakeholder = factory.LazyFunction(
        lambda: random.choice([True, False])  # nosec B311
    )
    windows = factory.LazyFunction(
        lambda: [WindowFactory() for _ in range(random.randint(1, 5))]  # nosec B311
    )
    networks = factory.LazyFunction(
        lambda: [
            generic.cyhy_provider.network_ipv4()
            for _ in range(random.randint(1, 5))  # nosec B311
        ]
    )
    scan_types = factory.LazyFunction(
        lambda: {
            random.choice(list(ScanType))  # nosec B311
            for _ in range(random.randint(1, 3))  # nosec B311
        }
    )


async def test_create_cves():
    """Test function to create and save 100 CVE instances."""
    for _ in range(100):
        cve = CVEFactory()
        print(cve)
        await cve.save()


async def test_create_request_docs():
    """Test function to create and save 100 RequestDoc instances."""
    for _ in range(100):
        request_doc = RequestDocFactory()
        print(request_doc)
        await request_doc.save()
