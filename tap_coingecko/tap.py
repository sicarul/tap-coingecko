"""Coingecko tap class."""

from importlib.metadata import requires
from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_coingecko.streams import (
    CoingeckoStream,
)

STREAM_TYPES = [
    CoingeckoStream
]


class TapCoingecko(Tap):
    """Coingecko tap class."""
    name = "tap-coingecko"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "token",
            th.StringType,
            required=True,
            description="The name of the token to import the price history of",
            default="ethereum"
        ),
        th.Property(
            "api_url",
            th.StringType,
            required=True,
            description="Coingecko's api url",
            default="https://api.coingecko.com/api/v3"
        ),
        th.Property(
            "start_date",
            th.StringType,
            required=True,
            description="First date to obtain token price for",
            default="2022-03-01"
        ),
        th.Property(
            "wait_time_between_requests",
            th.Integer,
            required=True,
            description="Number of seconds to wait between requests",
            default=5
        )
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
