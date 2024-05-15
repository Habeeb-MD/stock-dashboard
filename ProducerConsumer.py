import logging
import queue
import threading
import time

import data_fetch
from common_data import default_time_periods
from key_metrics import fetch_key_metrics
from quarterly_financials import fetch_financials
from ratios import _fetch_financial_ratio_for_single_symbol
from returns import calculate_returns
from stock_data import fetch_stock_data

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ProducerConsumer:
    def __init__(self, count):
        self.count = count
        self.queue = queue.Queue(
            maxsize=count * 11
        )  # multiplying by 11 because 11 is # of gics sectors
        self.event = threading.Event()

    def producer(self):
        """
        run_cache_update
        Updates cached data for a set of financial functions for top `count` stocks in the S&P 500 Index.

        Returns:
            str: Message indicating successful cache update with timestamp.
        """
        try:
            sector_wise_stock_symbol_and_weight_dict = (
                data_fetch.get_sector_wise_stock_symbol_and_weight()
            )
            functions_list = [
                data_fetch.info,
                data_fetch.annual_financials,
                data_fetch.annual_balance_sheet,
                data_fetch.quarterly_financials,
                data_fetch.quarterly_balance_sheet,
            ]

            for (
                sector,
                symbol_and_weight_list,
            ) in sector_wise_stock_symbol_and_weight_dict.items():
                if sector != "S&P 500 Index":
                    for symbol_and_weight in symbol_and_weight_list[: self.count]:
                        symbol = symbol_and_weight[0]
                        for func in functions_list:
                            func(symbol, force_update=True)
                        for period in default_time_periods.values():
                            data_fetch.history(symbol, period, force_update=True)

                        # putting this symbol in queue -> now consumer can consume/perform calc on this stock
                        self.queue.put(symbol)
                        logging.info("Producer :- added a new symbol: %s", symbol)

            logger.info("Producer : Finished its task. Exiting ....")
            # set this event to indicate that the producer is done with its task and now consumer can also quit
            # after finishing its calculations
            self.event.set()
            return f"Producer :- Successful Update @{time.ctime(time.time())}"

        except Exception as e:
            self.event.set()  # don't let the consumer waiting in case of error in producer
            logging.error(f"Failed to run cache update due to: {e}")

    def consumer(self):
        """Based on symbol present in Queue perform calculations"""

        # Run this until queue is not empty and event is not triggered
        while not self.event.is_set() or not self.queue.empty():
            symbol = self.queue.get()
            logging.info("Consumer :- calculating stats for symbol: %s", symbol)
            functions_list = [
                fetch_key_metrics,
                _fetch_financial_ratio_for_single_symbol,
                fetch_financials,
                calculate_returns,
                fetch_stock_data,
            ]
            for func in functions_list:
                func(symbol, force_update=True)

        logging.info("Consumer : Finished its task. Exiting ....")
        return f"Consumer :- Successful Update @{time.ctime(time.time())}"
