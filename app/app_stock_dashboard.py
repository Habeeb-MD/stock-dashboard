import concurrent.futures
import logging
import resource
import threading
import time

import streamlit as st
import streamlit_antd_components as sac

# Importing functions from other modules
import data_fetch
from CacheUpdater import CacheUpdater
from cacheUtil import CentralCache
from common_data import (
    industry_dataframe_default_cols,
    industry_dataframe_all_cols,
    all_time_periods,
    available_time_series,
    menus,
)
from key_metrics import display_key_metrics
from quarterly_financials import display_quarterly_stats
from ratios import display_financial_ratios
from returns import display_returns
from stock_data import fetch_multiple_stocks_data, display_industry_wide_stock_data
from time_series import fetch_time_series_data_and_plot
from utils import get_app_custom_config

# Set up the page configuration for Streamlit
st.set_page_config(layout="wide", page_title="Stock Dashboard")

# Create and configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)",
)
logging.VERBOSE = 5
logging.addLevelName(logging.VERBOSE, "VERBOSE")
logging.Logger.verbose = lambda inst, msg, *args, **kwargs: inst.log(
    logging.VERBOSE, msg, *args, **kwargs
)
logging.verbose = lambda msg, *args, **kwargs: logging.log(
    logging.VERBOSE, msg, *args, **kwargs
)
logger = logging.getLogger(__name__)

if get_app_custom_config("debug"):
    logger.setLevel(logging.DEBUG)


@st.cache_resource()
def get_data_cache_available_event_and_background_thread_detail():
    """
    This function is cached to prevent streamlit from creating more than one instance of shared_dict
    """
    logger.info("get_data_cache_available_event_and_background_thread_detail called...")
    _shared_dict = {
        "background_thread_detail": None,
        "data_cache_available_event": threading.Event(),  # "data_cache_available_event"
    }
    return _shared_dict


shared_dict = get_data_cache_available_event_and_background_thread_detail()
data_cache_available_event = shared_dict.get("data_cache_available_event")

st.title("Stock Dashboard | S&P500")

_cnt = get_app_custom_config("count")
_sleep_time = get_app_custom_config("sleep_time")


def background_task(count):
    while True:
        logger.info(
            f"background_task :- starting cache update @{time.ctime(time.time())}"
        )

        cache_updater = CacheUpdater(count)

        sector_wise_stock_symbol_and_weight_dict = (
            data_fetch.get_sector_wise_stock_symbol_and_weight()
        )
        sector_wise_stock_symbol_and_weight_list = list(
            sector_wise_stock_symbol_and_weight_dict.items()
        )

        with concurrent.futures.ProcessPoolExecutor() as executor:

            results = executor.map(
                cache_updater.update_cache,
                sector_wise_stock_symbol_and_weight_list,
            )

            # Print results of processing
            for result in results:
                logger.debug(result)

        # When both threads are done we can let the main thread know we are done updating the cache
        # and set the data_cache_available event if not already set
        if not data_cache_available_event.is_set():
            data_cache_available_event.set()
        logger.info("cache update finished")

        time.sleep(_sleep_time)


def start_background_task():
    _thread = threading.Thread(
        target=background_task,
        args=(_cnt,),
    )
    _thread.daemon = True  # Ensure the thread does not prevent the process from exiting
    logger.info(f"background_thread created @ {time.ctime(time.time())}")
    _thread.start()
    shared_dict["background_thread_detail"] = _thread.ident
    logger.debug(
        "background_thread_detail :- %d", shared_dict["background_thread_detail"]
    )


def start_app():
    # This will run only one time at start when application will start
    # Once the background_thread_event is set it will not run again.
    logger.debug(
        f"before Background task memory consumption {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}"
    )
    # initialize central cache
    CentralCache.initialise()
    start_background_task()
    st.success("Background task started.")
    time.sleep(30)
    logger.debug(
        f"after starting background task memory consumption {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}"
    )


# Function to verify password and start the background task
def verify_password():
    if st.session_state["password"] == st.secrets.credentials["password"]:
        start_app()
    else:
        st.error("Incorrect password.")


if get_app_custom_config("thread_details"):
    logger.debug(f"ACTIVE_THREAD_COUNT: {threading.active_count()}")
    for thread in threading.enumerate():
        logger.debug(f"{thread.name}, {thread.daemon}, {thread.ident}")

if not shared_dict.get("background_thread_detail"):
    # Password input
    if "password" not in st.session_state:
        st.session_state.password = ""

    if get_app_custom_config("environment") != "development":
        st.text_input(
            "Enter password to start Application:", type="password", key="password"
        )
        st.button("Submit", on_click=verify_password)
    else:
        start_app()
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
    with st.sidebar.container():
        # title
        st.subheader("Navigation")
        # menu
        menu = sac.menu(
            items=[sac.MenuItem(el) for el in menus],
            key="menu",
            open_all=True,
            indent=20,
            format_func="title",
        )

    # Define a function to delete the session state entry
    def delete_session_state_variable(*state_variables):
        for state_variable in state_variables:
            if state_variable in st.session_state:
                del st.session_state[state_variable]

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
                on_change=lambda: delete_session_state_variable(
                    "selected_tickers", "page_num", "entries_per_page"
                ),  # it's better to delete the "page_num", "entries_per_page" states on changing sectors because
                # number of tickers vary from sector to sector
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
    if menu == "Industry Data":
        # Layout configuration with Streamlit columns
        col1, col2, col3, col4 = st.columns([2, 1, 1, 3])
        with col1:
            sector_choice = st.selectbox(
                "Filter by Sector",
                sector_names,
                on_change=lambda: delete_session_state_variable(
                    "selected_tickers", "page_num", "entries_per_page"
                ),  # it's better to delete the "page_num", "entries_per_page" states on changing sectors because
                # number of tickers vary from sector to sector
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
                max_value=len(filtered_tickers_by_sector),
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

    elif menu == "Stock Details":
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

    elif menu == "Quarterly Financials":
        selected_stocks = sector_filter_and_ticker_selector()
        display_quarterly_stats(selected_stocks)

    elif menu == "Metrics":
        selected_stocks = sector_filter_and_ticker_selector()
        display_key_metrics(selected_stocks)

    elif menu == "Ratios":
        selected_stocks = sector_filter_and_ticker_selector()
        display_financial_ratios(selected_stocks)

    elif menu == "Returns":
        selected_stocks = sector_filter_and_ticker_selector()
        display_returns(selected_stocks)
