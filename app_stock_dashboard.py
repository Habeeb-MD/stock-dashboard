import logging
import queue
import threading
import time

import streamlit as st

import data_fetch
from common_data import (
    industry_dataframe_default_cols,
    industry_dataframe_all_cols,
    all_time_periods,
)
from key_metrics import display_key_metrics
from quarterly_financials import display_quarterly_stats
# Importing module functions
from ratios import display_financial_ratios
from returns import display_returns
from stock_data import fetch_multiple_stocks_data, display_industry_wide_stock_data
from time_series import fetch_time_series_data_and_plot

# Create and configure logger
logging.basicConfig(format="%(asctime)s %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Set up the page configuration for Streamlit
st.set_page_config(layout="wide", page_title="Stock Dashboard")


@st.cache_resource()
def get_queue():
    """
    This will return a variable which will be used for indicating that the cache has been updated successfully.
    Its value is set by background thread.
    This function is cached to prevent streamlit from creating more than one instance of data_queue
    """
    logger.info("get_queue called ..........")
    return queue.Queue(maxsize=1)


@st.cache_resource()
def get_background_thread_details():
    """
    This is for creating the background thread, It will be empty at the start and should be triggered only once.
    This function is cached to prevent streamlit from creating background thread more than once.
    """
    logger.info("get_last_update_detail called ..........")
    return list()


data_cache_available = get_queue()
background_thread_details = get_background_thread_details()


st.title("Sector-Based Stock Dashboard | S&P500")

_cnt = 10
_sleep_time = 3600


def background_task(cnt):
    while True:
        logger.info(
            f"background_task started for updating the cache @{time.ctime(time.time())}"
        )
        logger.info(data_fetch.run_cache_update(cnt))
        if data_cache_available.empty():
            data_cache_available.put("Cache updated successfully")
        logger.info("cache update finished")
        time.sleep(_sleep_time)


def start_background_task():
    thread = threading.Thread(
        target=background_task,
        args=(_cnt,),
    )
    thread.daemon = True  # Ensure the thread does not prevent the process from exiting
    thread.start()


if len(background_thread_details) == 0:
    # This will run only one time at start when application will start
    # Once the background_thread_details is filled it will not run again.
    logger.info("last_update_detail is empty")
    background_thread_details.append(
        f"background_thread created @ {time.ctime(time.time())}"
    )
    start_background_task()
    print(data_cache_available, background_thread_details)
    time.sleep(3 * 60)

if data_cache_available.qsize() == 0:
    st.write(
        "App is starting......\nPlease wait while cache update is in process......\nRefresh Page to check status"
    )
else:
    # Get SP500 tickers
    sector_wise_stock_symbol_and_weight = (
        data_fetch.get_sector_wise_stock_symbol_and_weight()
    )
    sector_names = data_fetch.get_gics_sector()

    # Initialize session state for tracking data fetching
    if "fetch_data" not in st.session_state:
        st.session_state.fetch_data = False

    def set_fetch_data():
        """Trigger for setting session state to indicate data needs to be fetched."""
        st.session_state.fetch_data = True

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
            value=_cnt,
        )
        total_pages = (len(filtered_tickers_by_sector) - 1) // entries_per_page + 1

    with col3:
        page = st.number_input(
            "Page", min_value=1, max_value=total_pages, value=1, step=1
        )

    with col4:
        popover = st.popover("Select Columns to Display")
        with popover:
            selected_columns = st.multiselect(
                "Choose Columns",
                options=industry_dataframe_all_cols,
                default=industry_dataframe_default_cols,
            )

    # filtered_tickers based on page
    start = (page - 1) * entries_per_page
    end = start + entries_per_page
    filtered_tickers_and_weight_by_sector_and_page_cnt = (
        filtered_tickers_and_weight_by_sector[start:end]
    )

    # fetch data for filtered_tickers on given page
    filtered_data = fetch_multiple_stocks_data(
        filtered_tickers_and_weight_by_sector_and_page_cnt
    )

    # Display the data table with industry data
    display_industry_wide_stock_data(filtered_data, selected_columns)

    # display page cnt
    st.write(f"Showing page {page} of {total_pages}")

    selected_stocks = st.multiselect(
        "Select stock symbols",
        filtered_tickers_by_sector,
        default=filtered_tickers_by_sector[: min(3, _cnt)],
    )

    # Time series and period selection for charts
    col1, col2 = st.columns(2)
    with col1:
        time_series = st.selectbox(
            "Select the time series data to plot",
            ["Open", "High", "Low", "Close", "Volume"],
            index=3,
        )

    with col2:
        time_frame = st.selectbox(
            "Select the time period for chart",
            all_time_periods.keys(),
            index=4,
        )
        time_frame = all_time_periods[time_frame]

    # Button to trigger data fetching and display
    if st.button("Fetch Data", on_click=set_fetch_data) or st.session_state.fetch_data:
        fetch_time_series_data_and_plot(selected_stocks, time_series, time_frame)
        display_key_metrics(selected_stocks)
        display_quarterly_stats(selected_stocks)
        display_financial_ratios(selected_stocks)
        display_returns(selected_stocks)
