# Standard Python Libraries
from datetime import datetime
import ipaddress
import random

# Third-Party Libraries
import factory
from mimesis import Generic
from mimesis.locales import DEFAULT_LOCALE
from mimesis.providers.base import BaseProvider
from mimesis_factory import MimesisField
from pytest_factoryboy import register

# cisagov Libraries
from cyhy_db.models import CVE, RequestDoc
from cyhy_db.models.enum import (
    AgencyType,
    CVSSVersion,
    DayOfWeek,
    PocType,
    ReportPeriod,
    ReportType,
    ScanType,
    Scheduler,
    Stage,
)
from cyhy_db.models.request_doc import Agency, Contact, Location, Window
from cyhy_db.utils import utcnow


class CyHyProvider(BaseProvider):
    class Meta:
        name = "cyhy_provider"

    def cve_id(self, year=None):
        # If year is None, generate a random year between 1999 and the current year
        if year is None:
            year = self.random.randint(1999, datetime.now().year)

        # Generate a random number for the CVE, ensuring it has a leading zero if necessary
        number = self.random.randint(1, 99999)

        return f"CVE-{year}-{number:05d}"

    def network_ipv4(self):
        # Generate a base IP address
        base_ip = generic.internet.ip_v4()
        # Choose a random CIDR between 24-30 to ensure a smaller network size and avoid host bits set error
        cidr = random.randint(24, 30)
        # Create the network address
        network = ipaddress.IPv4Network(f"{base_ip}/{cidr}", strict=False)
        return network


generic = Generic(locale=DEFAULT_LOCALE)
generic.add_provider(CyHyProvider)


@register
class CVEFactory(factory.Factory):
    class Meta:
        model = CVE

    id = factory.LazyFunction(lambda: generic.cyhy_provider.cve_id())
    cvss_score = factory.LazyFunction(lambda: round(random.uniform(0, 10), 1))
    cvss_version = factory.LazyFunction(lambda: random.choice(list(CVSSVersion)))
    severity = factory.LazyFunction(lambda: random.randint(1, 4))


class AgencyFactory(factory.Factory):
    class Meta:
        model = Agency

    name = factory.Faker("company")
    # Generate an acronym from the name
    acronym = factory.LazyAttribute(
        lambda o: "".join(word[0].upper() for word in o.name.split())
    )
    type = factory.LazyFunction(lambda: random.choice(list(AgencyType)))
    contacts = factory.LazyFunction(
        lambda: [ContactFactory() for _ in range(random.randint(1, 5))]
    )
    location = factory.LazyFunction(lambda: LocationFactory())


class ContactFactory(factory.Factory):
    class Meta:
        model = Contact

    email = factory.Faker("email")
    name = factory.Faker("name")
    phone = factory.Faker("phone_number")
    type = factory.LazyFunction(lambda: random.choice(list(PocType)))


class LocationFactory(factory.Factory):
    class Meta:
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
    class Meta:
        model = Window

    day = factory.LazyFunction(lambda: random.choice(list(DayOfWeek)))
    duration = factory.LazyFunction(lambda: random.randint(0, 168))
    start = factory.Faker("time", pattern="%H:%M:%S")


class RequestDocFactory(factory.Factory):
    class Meta:
        model = RequestDoc

    id = factory.LazyAttribute(
        lambda o: o.agency.acronym + "-" + str(random.randint(1, 1000))
    )
    agency = factory.SubFactory(AgencyFactory)
    enrolled = factory.LazyFunction(utcnow)
    init_stage = factory.LazyFunction(lambda: random.choice(list(Stage)))
    key = factory.Faker("password")
    period_start = factory.LazyFunction(utcnow)
    report_period = factory.LazyFunction(lambda: random.choice(list(ReportPeriod)))
    retired = factory.LazyFunction(lambda: random.choice([True, False]))
    scheduler = factory.LazyFunction(lambda: random.choice(list(Scheduler)))
    stakeholder = factory.LazyFunction(lambda: random.choice([True, False]))
    windows = factory.LazyFunction(
        lambda: [WindowFactory() for _ in range(random.randint(1, 5))]
    )
    networks = factory.LazyFunction(
        lambda: [
            generic.cyhy_provider.network_ipv4() for _ in range(random.randint(1, 5))
        ]
    )
    # create a set of 1 to 3 random scan types from the ScanType enum
    scan_types = factory.LazyFunction(
        lambda: {random.choice(list(ScanType)) for _ in range(random.randint(1, 3))}
    )


async def test_create_cves():
    for _ in range(100):
        cve = CVEFactory()
        print(cve)
        await cve.save()


async def test_create_request_docs():
    for _ in range(100):
        request_doc = RequestDocFactory()
        print(request_doc)
        await request_doc.save()
