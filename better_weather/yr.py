from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

import requests
from pydantic import BaseModel, Field, validator

from better_weather import __version__


class Location(BaseModel):
    name: str
    lat: float
    lon: float
    altitude: int

    @validator("lat", "lon")
    def no_more_than_four_decimals(cls, v: float):
        """
        Ensure lat/lon has less than 5 decimals.

        Ref: https://api.met.no/doc/TermsOfService
        """
        return round(v, 4)


class Units(BaseModel):
    air_pressure_at_sea_level: str
    air_temperature: str
    air_temperature_max: str
    air_temperature_min: str
    air_temperature_percentile_10: str
    air_temperature_percentile_90: str
    cloud_area_fraction: str
    cloud_area_fraction_high: str
    cloud_area_fraction_low: str
    cloud_area_fraction_medium: str
    dew_point_temperature: str
    fog_area_fraction: str
    precipitation_amount: str
    precipitation_amount_max: str
    precipitation_amount_min: str
    probability_of_precipitation: str
    probability_of_thunder: str
    relative_humidity: str
    ultraviolet_index_clear_sky: str
    wind_from_direction: str
    wind_speed: str
    wind_speed_of_gust: str
    wind_speed_percentile_10: str
    wind_speed_percentile_90: str


class ForecastInstant(BaseModel):
    class ForecastInstantDetails(BaseModel):
        wind_from_direction: Optional[float]
        cloud_area_fraction: Optional[float]
        wind_speed_of_gust: Optional[float]
        air_pressure_at_sea_level: Optional[float]
        relative_humidity: Optional[float]
        wind_speed: Optional[float]
        air_temperature: Optional[float]
        cloud_area_fraction_high: Optional[float]
        cloud_area_fraction_medium: Optional[float]
        cloud_area_fraction_low: Optional[float]
        dew_point_temperature: Optional[float]
        fog_area_fraction: Optional[float]

    details: ForecastInstantDetails


class ForecastDetails(BaseModel):
    probability_of_thunder: Optional[float]
    probability_of_precipitation: Optional[float]
    ultraviolet_index_clear_sky_max: Optional[float]
    air_temperature_max: Optional[float]
    precipitation_amount: Optional[float]
    precipitation_amount_max: Optional[float]
    precipitation_amount_min: Optional[float]
    air_temperature_min: Optional[float]


class ForecastSummary(BaseModel):
    symbol_code: str
    symbol_confidence: Optional[str]


class Forecast(BaseModel):
    summary: ForecastSummary
    details: ForecastDetails


class Timeseries(BaseModel):
    time: datetime
    instant: ForecastInstant
    next_1_hours: Optional[Forecast]
    next_6_hours: Optional[Forecast]
    next_12_hours: Optional[Forecast]

    # @validator("time")
    # def timezone_aware(cls, v: datetime):
    #     """Make the timestamp aware of its timezone (UTC)."""
    #     return pytz.utc.localize(v)


class ForecastResponse(BaseModel):
    location: Location
    request_timestamp: datetime = Field(
        default_factory=lambda: datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
    )
    updated_at: datetime
    expires_at: datetime
    units: Units
    timeseries: list[Timeseries]

    @validator("request_timestamp", "expires_at")
    def timezone_aware(cls, v: datetime):
        """Make the timestamp aware of its timezone (UTC)."""
        return v.replace(tzinfo=ZoneInfo("UTC"))


def get_forecast(location: Location) -> ForecastResponse:
    response = requests.get(
        "https://api.met.no/weatherapi/locationforecast/2.0/complete",
        params=location.dict(exclude={"name"}),
        headers={
            "User-Agent": f"better-weather/{__version__} github.com/bsamseth/better-weather"
        },
    )
    response.raise_for_status()
    data = response.json()["properties"]
    return ForecastResponse(
        location=location,
        expires_at=datetime.strptime(
            response.headers["Expires"], "%a, %d %b %Y %H:%M:%S %Z"
        ),
        updated_at=data["meta"]["updated_at"],
        units=data["meta"]["units"],
        timeseries=[{"time": t["time"]} | t["data"] for t in data["timeseries"]],
    )
