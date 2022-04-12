"""Stream type classes for tap-coingecko."""

import pendulum, requests, time, logging, copy, backoff
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable, cast, Callable

from singer_sdk import typing as th  # JSON Schema typing helpers
from singer_sdk.exceptions import FatalAPIError, RetriableAPIError


from singer_sdk.streams import RESTStream

class CoingeckoStream(RESTStream):
    name = "coingecko_token"

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config["api_url"]

    @property
    def path(self) -> str:
        return f"/coins/{self.config['token']}/history"

    primary_keys = ['date']
    replication_key = 'date'
    replication_method = "INCREMENTAL"
    is_sorted = True

    def request_decorator(self, func: Callable) -> Callable:
        decorator: Callable = backoff.on_exception(
            backoff.expo,
            (
                RetriableAPIError,
                requests.exceptions.ReadTimeout,
            ),
            max_tries=8,
            factor=3,
        )(func)
        return decorator


    def request_records(self, context: Optional[dict]) -> Iterable[dict]:
        next_page_token: Any = self.get_next_page_token(None, None, context)
        if not next_page_token:
            return
        
        finished = False
        decorated_request = self.request_decorator(self._request)

        while not finished:
            prepared_request = self.prepare_request(
                context, next_page_token=next_page_token
            )
            resp = decorated_request(prepared_request, context)
            for row in self.parse_response(resp, next_page_token):
                yield row
            previous_token = copy.deepcopy(next_page_token)
            next_page_token = self.get_next_page_token(
                response=resp, previous_token=previous_token, context=context
            )
            if next_page_token and next_page_token == previous_token:
                raise RuntimeError(
                    f"Loop detected in pagination. "
                    f"Pagination token {next_page_token} is identical to prior token."
                )
            # Cycle until get_next_page_token() no longer returns a value
            finished = not next_page_token
            if not finished:
                time.sleep(1.1) # Wait 1.1s before next request


    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any], context: Optional[dict]
    ) -> Any:
        """Return token identifying next page or None if all records have been read."""
        

        old_token = previous_token or self.get_starting_replication_key_value(context) or self.config["coingecko_start_date"]
        if isinstance(old_token, str):
            old_token = cast(datetime, pendulum.parse(old_token))
        signpost = self.get_replication_key_signpost(context)
        
        if old_token < signpost:
            next_page_token = old_token + timedelta(days=1)
            self.logger.info(f"Next page: {next_page_token}")
            return next_page_token
        else:
            return None

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any] = None
    ) -> Dict[str, Any]:
        return {"date": next_page_token.strftime('%d-%m-%Y'), "localization": "false"}
       

    def get_replication_key_signpost(
        self, context: Optional[dict]
    ) -> Optional[Union[datetime, Any]]:
        return cast(datetime, pendulum.yesterday(tz='UTC'))



    def parse_response(self, response, next_page_token) -> Iterable[dict]:
        resp_json = response.json()
        resp_json['date'] = next_page_token
        yield resp_json #Only one row per query

    def post_process(self, row: dict, context: Optional[dict] = None) -> dict:
        market_data = row.get('market_data')
        
        if market_data:
            row['price_usd'] = market_data.get('current_price').get('usd')
            row['market_cap_usd'] = market_data.get('market_cap').get('usd')
            row['total_volume_usd'] = market_data.get('total_volume').get('usd')
        
        row['date'] = row['date'].strftime("%Y-%m-%d")
        return row



    schema = th.PropertiesList(
        th.Property("date", th.StringType, required=True),
        th.Property("price_usd", th.NumberType),
        th.Property("market_cap_usd", th.NumberType),
        th.Property("total_volume_usd", th.NumberType),
        th.Property("community_data", th.ObjectType(
            th.Property("twitter_followers", th.NumberType),
            th.Property("reddit_average_posts_48h", th.NumberType),
            th.Property("reddit_average_comments_48h", th.NumberType),
            th.Property("reddit_subscribers", th.NumberType),
            th.Property("reddit_accounts_active_48h", th.StringType),
        )),
        th.Property("public_interest_stats", th.ObjectType(
            th.Property("alexa_rank", th.NumberType),
        ))
    ).to_dict()

