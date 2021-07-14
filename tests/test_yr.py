from datetime import datetime

from better_weather.yr import Location, get_forecast

OSLO = Location(name="Oslo (Blindern)", lat=59.9423, lon=10.72, altitude=94)


def test_yr_get_forecast():
    """
    Aquire forecast for OSLO.

    This makes some basic assertions on the various timestamps.
    Otherwise, all the data in the actual forecast is validated automatically."""
    forecast = get_forecast(OSLO)

    assert forecast.location == OSLO
    assert (
        forecast.updated_at
        < forecast.request_timestamp
        <= datetime.utcnow()
        < forecast.expires_at
    )
    assert forecast.timeseries
