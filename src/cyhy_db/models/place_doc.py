"""The model for place documents."""

# Standard Python Libraries
from typing import Optional

# Third-Party Libraries
from beanie import Document
from pydantic import ConfigDict, Field


class PlaceDoc(Document):
    """The place document model."""

    model_config = ConfigDict(extra="forbid")

    class_: str = Field(alias="class")  # 'class' is a reserved keyword in Python
    country_name: str
    country: str
    county_fips: Optional[str] = None
    county: Optional[str] = None
    elevation_feet: Optional[int] = None
    elevation_meters: Optional[int] = None
    # See: https://github.com/cisagov/cyhy-db/issues/7
    # GNIS FEATURE_ID (INCITS 446-2008) - https://geonames.usgs.gov/domestic/index.html
    id: int = Field(default_factory=int)  # type: ignore[assignment]
    latitude_dec: float
    latitude_dms: Optional[str] = None
    longitude_dec: float
    longitude_dms: Optional[str] = None
    name: str
    state_fips: str
    state_name: str
    state: str

    class Settings:
        """Beanie settings."""

        name = "places"
