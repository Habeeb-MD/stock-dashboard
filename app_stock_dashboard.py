import concurrent.futures
import logging
import threading
import time

import requests
import streamlit as st

import data_fetch
from ProducerConsumer import ProducerConsumer
from common_data import (
    industry_dataframe_default_cols,
    industry_dataframe_all_cols,
    all_time_periods,
    available_time_series,
)
from key_metrics import display_key_metrics
from quarterly_financials import display_quarterly_stats
# Importing functions from other modules
from ratios import display_financial_ratios
from returns import display_returns
from stock_data import fetch_multiple_stocks_data, display_industry_wide_stock_data
from time_series import fetch_time_series_data_and_plot

# Create and configure logger
logging.basicConfig(format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Set up the page configuration for Streamlit
st.set_page_config(layout="wide", page_title="Stock Dashboard")


@st.cache_resource()
def get_thread_event(event_name):
    """
    This function is cached to prevent streamlit from creating more than one instance of data_queue
    """
    logger.info(f"get_thread_event called for {event_name}..........")
    return threading.Event()


# This is for creating the background thread, It should be triggered only once.
# If this event is set, it means that the background thread is already exist.
background_thread_event = get_thread_event("start_background_thread")

# This will return an event which will be used for indicating that the cache is available.
# Its value is set by background thread.
data_cache_available_event = get_thread_event("data_cache_available")

st.title("Stock Dashboard | S&P500")

_cnt = 10
_sleep_time = 3600


def check_server_health():
    url = "https://stocks-dashboard-sp500.streamlit.app/"
    response = requests.get(url)
    assert response.status_code == 200
    logger.info("server is ok")


def background_task(count):
    while True:
        logger.info(
            f"background_task started for updating the cache @{time.ctime(time.time())}"
        )

        producer_consumer = ProducerConsumer(count)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_method = {
                executor.submit(producer_consumer.producer): "producer_future",
                executor.submit(producer_consumer.consumer): "consumer_future",
            }
            # This will yield future result as they are finished
            for future in concurrent.futures.as_completed(future_to_method):
                method = future_to_method[future]
                data = future.result()
                logger.info(method + "->" + data)

        # When both threads are done we can let the main thread know we are done updating the cache
        # and set the data_cache_available event if not already set
        if not data_cache_available_event.is_set():
            data_cache_available_event.set()
        logger.info("cache update finished")
        check_server_health()
        time.sleep(_sleep_time)


def start_background_task():
    thread = threading.Thread(
        target=background_task,
        args=(_cnt,),
    )
    thread.daemon = True  # Ensure the thread does not prevent the process from exiting
    logger.info(f"background_thread created @ {time.ctime(time.time())}")
    thread.start()


if not background_thread_event.is_set():
    # This will run only one time at start when application will start
    # Once the background_thread_event is set it will not run again.
    logger.info("background_thread_event is not set")
    background_thread_event.set()
    start_background_task()
    print(data_cache_available_event, background_thread_event)
    time.sleep(3 * 60)

if not data_cache_available_event.is_set():
    st.write(
        "App is starting......  \nPlease wait while cache update is in process......  \nRefresh Page to check status"
    )
else:

    # Initialize session state for tracking selected_columns,selected tickers,time period,time series,page_num and
    # entries_per_page
    if "selected_columns" not in st.session_state:
        st.session_state.selected_columns = industry_dataframe_default_cols
    if "selected_time_period_index" not in st.session_state:
        st.session_state.selected_time_period_index = 4  # for ytd
    if "selected_time_series_index" not in st.session_state:
        st.session_state.selected_time_series_index = 3  # close
    if "page_num" not in st.session_state:
        st.session_state.page_num = 1
    if "entries_per_page" not in st.session_state:
        st.session_state.entries_per_page = _cnt

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    section = st.sidebar.radio(
        "Go to",
        [
            "Industry Data",
            "Stock Details",
            "Financials",
            "Metrics",
            "Ratios",
            "Returns",
        ],
    )

    # Get SP500 tickers
    sector_wise_stock_symbol_and_weight = (
        data_fetch.get_sector_wise_stock_symbol_and_weight()
    )
    sector_names = data_fetch.get_gics_sector()

    def sector_filter_and_ticker_selector():
        col1, col2 = st.columns([2, 2])
        with col1:
            sector_choice = st.selectbox(
                "Filter by Sector",
                sector_names,
            )
        # Apply sector filter to tickers
        filtered_tickers_and_weight_by_sector = sector_wise_stock_symbol_and_weight.get(
            sector_choice
        )
        filtered_tickers_by_sector = list(
            map(
                lambda ticker_and_weight: ticker_and_weight[0],
                filtered_tickers_and_weight_by_sector,
            )
        )
        if "selected_tickers" not in st.session_state:
            st.session_state.selected_tickers = filtered_tickers_by_sector[
                : min(3, _cnt)
            ]
        with col2:
            selected_stocks = st.multiselect(
                "Select stock symbols",
                filtered_tickers_by_sector,
                default=st.session_state.selected_tickers,
            )
        st.session_state.selected_tickers = selected_stocks
        return selected_stocks

    # Navigation handling
    if section == "Industry Data":
        # Layout configuration with Streamlit columns
        col1, col2, col3, col4 = st.columns([2, 1, 1, 3])
        with col1:
            sector_choice = st.selectbox(
                "Filter by Sector",
                sector_names,
            )

        # Apply sector filter to tickers
        filtered_tickers_and_weight_by_sector = sector_wise_stock_symbol_and_weight.get(
            sector_choice
        )
        filtered_tickers_by_sector = list(
            map(
                lambda ticker_and_weight: ticker_and_weight[0],
                filtered_tickers_and_weight_by_sector,
            )
        )
        with col2:
            entries_per_page = st.number_input(
                "Results per Page",
                min_value=1,
                max_value=len(filtered_tickers_by_sector) + 10,
                value=st.session_state.entries_per_page,
            )
            st.session_state.entries_per_page = entries_per_page
            total_pages = (len(filtered_tickers_by_sector) - 1) // entries_per_page + 1

        with col3:
            page = st.number_input(
                "Page",
                min_value=1,
                max_value=total_pages,
                value=st.session_state.page_num,
                step=1,
            )
            st.session_state.page_num = page

        with col4:
            popover = st.popover("Select Columns to Display")
            with popover:
                selected_columns = st.multiselect(
                    "Choose Columns",
                    options=industry_dataframe_all_cols,
                    default=st.session_state.selected_columns,
                )
                # saving state
                st.session_state.selected_columns = selected_columns

        # filtered_tickers based on page number and entries_per_page
        start = (page - 1) * entries_per_page
        end = start + entries_per_page
        filtered_tickers_and_weight_by_sector_and_page_cnt = (
            filtered_tickers_and_weight_by_sector[start:end]
        )

        # fetch data for filtered_tickers on given page
        filtered_data = fetch_multiple_stocks_data(
            filtered_tickers_and_weight_by_sector_and_page_cnt
        )

        st.header("Industry Data")
        # Display the data table with industry data
        display_industry_wide_stock_data(filtered_data, selected_columns)
        st.write(f"Showing page {page} of {total_pages}")

    elif section == "Stock Details":
        selected_stocks = sector_filter_and_ticker_selector()

        # Time series and period selection for charts
        col1, col2 = st.columns(2)
        with col1:
            time_series = st.selectbox(
                "Select the time series data to plot",
                available_time_series,
                index=st.session_state.selected_time_series_index,
            )
            # saving state
            st.session_state.selected_time_series_index = available_time_series.index(
                time_series
            )

        with col2:
            time_frame = st.selectbox(
                "Select the time period for chart",
                all_time_periods.keys(),
                index=st.session_state.selected_time_period_index,
            )
            # saving state
            st.session_state.selected_time_period_index = list(
                all_time_periods.keys()
            ).index(time_frame)

            time_frame = all_time_periods[time_frame]

        fetch_time_series_data_and_plot(selected_stocks, time_series, time_frame)

    elif section == "Financials":
        selected_stocks = sector_filter_and_ticker_selector()
        display_quarterly_stats(selected_stocks)

    elif section == "Metrics":
        selected_stocks = sector_filter_and_ticker_selector()
        display_key_metrics(selected_stocks)

    elif section == "Ratios":
        selected_stocks = sector_filter_and_ticker_selector()
        display_financial_ratios(selected_stocks)

    elif section == "Returns":
        selected_stocks = sector_filter_and_ticker_selector()
        display_returns(selected_stocks)
