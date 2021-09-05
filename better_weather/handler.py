from typing import Any

import boto3

from better_weather.yr import Location, get_forecast

locations = {
    "oslo": Location(name="Oslo (Blindern)", lat=59.9423, lon=10.72, altitude=94),
}


def handler(event: dict[str, Any], context: Any) -> None:
    s3 = boto3.client("s3", region_name="eu-west-1")

    for loc_name, location in locations.items():
        forecast = get_forecast(location)
        s3.put_object(
            Bucket="bsamseth-better-weather",
            Body=forecast.json(),
            Key=f"yr/{loc_name}/{forecast.updated_at.isoformat()}.json",
            ContentType="application/json",
        )
