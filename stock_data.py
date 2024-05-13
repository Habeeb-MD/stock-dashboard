import streamlit as st
import pandas as pd
import data_fetch
from common_data import stock_dataframe_column_config


def calculate_return_on_capital_employed(symbol):
    """
    Calculate the Return on Capital Employed (ROCE) for a given stock symbol.
    Annualized ROCE % calculation for the fiscal year that ended in Jun. 2023
    https://www.gurufocus.com/term/roce/MSFT

    Parameters:
        symbol (str): The stock symbol to query ROCE for.

    Returns:
        float: The ROCE percentage for the latest fiscal year available.

    Raises:
        ValueError: If required financial data is missing.
    """
    try:
        fin_data = data_fetch.annual_financials(symbol)
        balance_sheet = data_fetch.annual_balance_sheet(symbol)

        ebit = fin_data.loc["EBIT"].iloc[0]
        total_assets = balance_sheet.loc["Total Assets"].dropna()
        current_liabilities = balance_sheet.loc["Current Liabilities"].dropna()

        if len(total_assets) < 2 or len(current_liabilities) < 2:
            raise ValueError(
                "Insufficient data to calculate averages for assets or liabilities."
            )

        avg_total_assets = (total_assets.iloc[0] + total_assets.iloc[1]) / 2
        avg_current_liabilities = (
            current_liabilities.iloc[0] + current_liabilities.iloc[1]
        ) / 2
        avg_capital_employed = avg_total_assets - avg_current_liabilities

        if avg_capital_employed == 0:
            return 0

        roce = (ebit / avg_capital_employed) * 100
        return roce

    except KeyError as e:
        print(
            f"Unable to calculate ROCE for {symbol}, Required financial information is missing: {e}"
        )
        return None


def fetch_stock_data(symbol):
    """
    Fetches a variety of financial details for a given stock symbol.
    Fetches a variety of financial details for a given stock symbol.

    Parameters:
        symbol (str): The stock symbol.

    Returns:
        dict: A dictionary containing various financial details of the stock.
    """

    try:
        stock_info = data_fetch.info(symbol)
        quarterly_financials = data_fetch.quarterly_financials(symbol)

        data = {
            "Symbol": symbol,
            "Name": stock_info.get("shortName"),
            "Sector": stock_info.get("sector"),
            "Current Price": stock_info.get("previousClose"),
            "Price to Earning": stock_info.get("trailingPE"),
            "Market Capitalization": stock_info.get("marketCap"),
            "Dividend Yield": stock_info.get("dividendYield"),
            "Net Income Latest Quarter": quarterly_financials.loc["Net Income"].iloc[0],
            "YOY Quarterly Profit Growth": stock_info.get("earningsQuarterlyGrowth"),
            "Sales Latest Quarter": quarterly_financials.loc["Total Revenue"].iloc[0],
            "YOY Quarterly Sales Growth": stock_info.get("revenueGrowth"),
            "Return on Capital Employed": calculate_return_on_capital_employed(symbol),
            "Debt to Equity": stock_info.get("debtToEquity"),
        }
        return data

    except Exception as e:
        st.warning(f"Failed to fetch data for {symbol}: {e}")
        return {}


def fetch_multiple_stocks_data(symbols):
    """
    Fetches stock data for multiple symbols.
    Calls the fetch_stock_data for every stock and returns the combined result

    Parameters:
        symbols (list of str): List of stock symbols.

    Returns:
        pandas.DataFrame: A DataFrame containing collected stock data.
    """
    stock_details = []
    for symbol in symbols:
        dt = fetch_stock_data(symbol)
        if dt:
            stock_details.append(dt)
    return pd.DataFrame(stock_details)


def display_industry_wide_stock_data(filtered_data, selected_columns):
    """
    Displays info for all stock in an industry

    Parameters:
        filtered_data (pandas.DataFrame): The data to display.
        selected_columns (list of str): Columns to display.
    """
    # Prepare the data for display

    # convert to a billion
    for column in [
        "Market Capitalization",
        "Net Income Latest Quarter",
        "Sales Latest Quarter",
    ]:
        # Safe conversion handling None values using .apply() and lambda
        filtered_data[column] = filtered_data[column].apply(
            lambda x: x / 1e9 if x else None
        )

    # convert to percentage
    for column in [
        "Dividend Yield",
        "YOY Quarterly Profit Growth",
        "YOY Quarterly Sales Growth",
    ]:
        filtered_data[column] = filtered_data[column].apply(
            lambda x: x * 100 if x else None
        )

    st.dataframe(
        filtered_data[selected_columns],
        use_container_width=True,
        hide_index=True,
        column_config=stock_dataframe_column_config,
    )
