import logging
import os
import time

import data_fetch
from common_data import default_time_periods
from key_metrics import fetch_key_metrics
from quarterly_financials import fetch_financials
from ratios import _fetch_financial_ratio_for_single_symbol
from returns import calculate_returns
from stock_data import fetch_stock_data, calculate_return_on_capital_employed
from utils import get_app_custom_config

logger = logging.getLogger(__name__)
if get_app_custom_config("cache_updater_details"):
    logger.setLevel(logging.DEBUG)


class CacheUpdater:
    def __init__(self, count):
        self.count = count

    def update_cache(self, args):
        """
        Updates cached data for a set of functions for top `count` stocks in the given sector.

        Returns:
            str: Message indicating successful cache update with timestamp.
        """
        sector, symbol_and_weight_list = args
        logger.debug("CacheUpdater :- Updating cached data for sector %s", sector)
        try:
            producer_functions_list = [
                data_fetch.info,
                data_fetch.annual_financials,
                data_fetch.annual_balance_sheet,
                data_fetch.quarterly_financials,
                data_fetch.quarterly_balance_sheet,
            ]
            for symbol_and_weight in symbol_and_weight_list[: self.count]:
                symbol = symbol_and_weight[0]
                for func in producer_functions_list:
                    func(symbol, force_update=True)
                for period in default_time_periods.values():
                    data_fetch.history(symbol, period, force_update=True)

                consumer_functions_list = [
                    calculate_return_on_capital_employed,
                    fetch_stock_data,
                    fetch_key_metrics,
                    _fetch_financial_ratio_for_single_symbol,
                    fetch_financials,
                    calculate_returns,
                ]
                for func in consumer_functions_list:
                    func(symbol, force_update=True)

        except Exception as e:
            logger.error(
                f"CacheUpdater @process:- {os.getpid()} : Failed to run cache update for sector {sector} due to: {e}"
            )
            return f"CacheUpdater @process:- {os.getpid()} : Failed to run cache update for sector {sector} due to: {e}"

        logger.debug(
            f"CacheUpdater @process:- {os.getpid()} :- Finished its task for sector {sector}. Exiting ...."
        )
        return f"CacheUpdater @process:- {os.getpid()}  :- Successful Update for sector {sector} @{time.ctime(time.time())}"
