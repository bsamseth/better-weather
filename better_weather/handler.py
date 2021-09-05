from typing import Any

import boto3

from better_weather.yr import Location, get_forecast


def handler(event: dict[str, Any], context: Any) -> None:
    OSLO = Location(name="Oslo (Blindern)", lat=59.9423, lon=10.72, altitude=94)
    forecast = get_forecast(OSLO)

    s3 = boto3.client("s3", region_name="eu-west-1")
    s3.put_object(
        Bucket="bsamseth-better-weather",
        Body=forecast.json(),
        Key=f"yr/oslo/{forecast.updated_at.isoformat()}.json",
        ContentType="application/json",
    )
