import streamlit as st
import pandas as pd

import data_fetch
from common_data import financial_columns_renamed, financial_columns


def fetch_financials(symbol):
    """
    Fetches the most recent quarterly financials for a given stock symbol.

    Parameters:
        symbol (str): The stock symbol for which to fetch quarterly financials.

    Returns:
        dict: A dictionary containing the latest quarterly financial data for the specified symbol.
    """
    try:
        financials = data_fetch.quarterly_financials(symbol)
        if financials is not None and not financials.empty:
            data = {}
            fin_data = financials.iloc[:, 0]  # Most recent quarter is the first column
            for col in financial_columns:
                data[col] = fin_data.get(col, None)
            for col, renamed in financial_columns_renamed.items():
                data[renamed] = fin_data.get(col, None)
            return data
        else:
            st.warning(f"No quarterly financials available for {symbol}.")
            return {
                key: None
                for key in (
                    financial_columns + list(financial_columns_renamed.values())
                )
            }
    except Exception as e:
        st.error(f"Error fetching quarterly financials for {symbol}: {str(e)}")
        return {
            key: None
            for key in (financial_columns + list(financial_columns_renamed.values()))
        }


def display_quarterly_stats(selected_stocks):
    """
    Displays the latest quarterly financial statistics for a list of selected stocks.

    Parameters:
        selected_stocks (list of str): List of stock symbols to fetch data for.
    """
    st.subheader("Quarterly Financials")
    data = {stock: fetch_financials(stock) for stock in selected_stocks}
    # Converting to DataFrame
    financial_df = pd.DataFrame(data)
    if not financial_df.empty:
        st.dataframe(financial_df, use_container_width=True)
    else:
        st.write("No financial data to display.")
