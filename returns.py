import streamlit as st
import pandas as pd

import data_fetch
from common_data import default_time_periods


def calculate_returns(symbol, periods=None):
    """
    Calculates the cumulative returns for different time periods for a given stock symbol.

    Args:
        symbol (str): The stock symbol.
        periods (dict): A dictionary of time periods and their abbreviations(codes).

    Returns:
        dict: Returns a dictionary with time periods as keys and formatted cumulative returns as values.
    """
    if periods is None:
        periods = default_time_periods
    returns = {}
    for period, period_abbreviation in periods.items():
        hist = data_fetch.history(symbol, period_abbreviation)
        if not hist.empty:
            hist["Daily Returns"] = hist["Close"].pct_change()
            hist["Cumulative Returns"] = (
                1 + hist["Daily Returns"].iloc[1:]
            ).cumprod() - 1
            cumulative_returns = hist["Cumulative Returns"].iloc[-1] * 100
            returns[period + " Returns"] = f"{cumulative_returns:.2f} %"
        else:
            returns[period + " Returns"] = None
    return returns


def display_returns(selected_stocks):
    """
    Displays the stock performance returns for a list of selected stocks.

    Args:
        selected_stocks (list of str): A list of stock symbols.
    """
    st.subheader("Performance")
    returns_data = {stock: calculate_returns(stock) for stock in selected_stocks}
    returns_df = pd.DataFrame(returns_data).transpose()
    returns_df.index.name = "Symbol"
    st.dataframe(returns_df, use_container_width=True)
