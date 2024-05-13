import pandas as pd
import streamlit as st

import data_fetch
from stock_data import calculate_return_on_capital_employed


def fetch_key_metrics(symbol):
    """
    Fetch and return key financial metrics for a given stock symbol.

    Parameters:
        symbol (str): The stock symbol for which to fetch metrics.

    Returns:
        dict: A dictionary containing key financial metrics.
    """
    try:
        stock_info = data_fetch.info(symbol)
        metrics = {
            "Market Cap (USD)": stock_info.get("marketCap"),
            "Return on Equity % (ttm)": (
                stock_info.get("returnOnEquity") * 1e2
                if stock_info.get("returnOnEquity")
                else None
            ),
            "Return on Assets % (ttm)": (
                stock_info.get("returnOnAssets") * 1e2
                if stock_info.get("returnOnAssets")
                else None
            ),
            "Trailing P/E Ratio (ttm)": stock_info.get("trailingPE"),
            "Forward P/E Ratio": stock_info.get("forwardPE"),
            "Price/Book (mrq)": stock_info.get("priceToBook"),
            "Price/Sales (ttm)": stock_info.get("priceToSalesTrailing12Months"),
            "Dividend Yield": stock_info.get("dividendYield"),
            "Outstanding Shares": stock_info.get("sharesOutstanding"),
            "Diluted EPS (ttm)": stock_info.get("trailingEps"),
            "PEG Ratio (5yr expected)": stock_info.get("pegRatio"),
            "Enterprise Value/Revenue": stock_info.get("enterpriseToRevenue"),
            "Total Debt (mrq) USD": stock_info.get("totalDebt"),
            "Total Debt/Equity (mrq)": stock_info.get("debtToEquity"),
            "Current Ratio (mrq)": stock_info.get("currentRatio"),
            "Return on Capital Employed": calculate_return_on_capital_employed(symbol),
        }
        return metrics
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return {}


def display_key_metrics(selected_stocks):
    """
    Display a DataFrame of key metrics for selected stocks in the Streamlit app.

    Parameters:
        selected_stocks (list of str): List of stock symbols.
    """
    st.subheader("Key Metrics")
    data = [fetch_key_metrics(symbol) for symbol in selected_stocks]
    if any(data):
        key_metrics_data = pd.DataFrame(data, index=selected_stocks)
        st.dataframe(
            key_metrics_data.transpose().rename_axis("Metrics"),
            use_container_width=True,
        )
    else:
        st.write("No data available for selected stocks.")
