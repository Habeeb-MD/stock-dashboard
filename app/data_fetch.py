import logging
from io import StringIO

import pandas as pd
import requests
import yfinance as yf

from cacheUtil import cached_with_force_update

logger = logging.getLogger(__name__)


@cached_with_force_update()
def get_tickers_sector():
    """
    Fetches the tickers and sectors for S&P 500 companies from Wikipedia.

    Returns:
        pandas.DataFrame: DataFrame indexed by 'Symbol' with a column for 'GICS Sector'.

    Raises:
        Exception: Raises an exception if the data cannot be fetched or parsed.
    """
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        data = pd.read_html(url)[0]
        tickers_sector = data[["Symbol", "GICS Sector"]].set_index("Symbol")
        return tickers_sector
    except Exception as e:
        logger.error(f"Failed to fetch or parse ticker data from Wikipedia: {e}")


@cached_with_force_update()
def get_tickers_weight():
    """
    Fetches the tickers and their portfolio weights for S&P 500 companies from SlickCharts.

    Returns:
        pandas.DataFrame: DataFrame indexed by 'Symbol' with a column for 'Portfolio%'.

    Raises:
        Exception: Raises an exception if the data cannot be fetched or parsed.
    """
    try:
        url = "https://www.slickcharts.com/sp500"
        headers = {"User-Agent": "PostmanRuntime/7.38.0"}
        response = requests.get(url, headers=headers)
        data = pd.read_html(StringIO(response.text))[0]
        tickers_weight = data[["Symbol", "Weight"]].set_index("Symbol")
        return tickers_weight
    except requests.RequestException as e:
        logger.error(f"HTTP error occurred: {e}")
    except ValueError as e:
        logger.error(f"Error parsing the HTML: {e}")


@cached_with_force_update()
def get_gics_sector():
    """
    Fetches unique GICS sectors from the S&P 500 list of companies.

    Returns:
        list: A list of unique GICS sectors

    Raises:
        Exception: Raises an exception if the required data is not accessible or if there's an unexpected structure.
    """
    try:
        tickers_sector = get_tickers_sector()
        gics_sector = ["S&P 500 Index"] + list(tickers_sector["GICS Sector"].unique())
        return gics_sector
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


@cached_with_force_update()
def get_sector_wise_stock_symbol_and_weight():
    """
    Combines sector and weight information of S&P 500 companies into a structured dictionary.

    Returns:
        dict: A dictionary with sectors as keys and lists of tuples (Symbol, Weight) as values.

    Raises:
        Exception: Raises an exception if the required data is not accessible or if there's an unexpected structure.
    """
    try:
        tickers_sector = get_tickers_sector()
        tickers_weight = get_tickers_weight()

        # Merging data on 'Symbol' index
        tickers_weight_sector = pd.concat(
            [tickers_sector, tickers_weight], axis=1, join="inner"
        )
        tickers_weight_sector["Portfolio%"] = (
            tickers_weight_sector["Weight"].str.rstrip("%").astype(float)
        )
        tickers_weight_sector = tickers_weight_sector.sort_values(
            by="Portfolio%", ascending=False
        )

        sector_wise_stock_symbol_and_weight_dict = {
            "S&P 500 Index": tickers_weight_sector
        }
        sector_wise_stock_symbol_and_weight_dict.update(
            dict(tuple(tickers_weight_sector.groupby("GICS Sector")))
        )
        sector_wise_stock_symbol_and_weight_dict = {
            sector: list(map(tuple, df["Portfolio%"].reset_index().values))
            for sector, df in sector_wise_stock_symbol_and_weight_dict.items()
        }
        return sector_wise_stock_symbol_and_weight_dict
    except Exception as e:
        logger.error(
            f"Failed to generate sector-wise stock symbol and weight data: {e}"
        )


@cached_with_force_update()
def history(symbol, period):
    """
    Fetches historical stock data for a given symbol over a specified period.

    Parameters:
        symbol (str): The stock symbol.
        period (str): The period over which historical data is requested (e.g., '1mo', '1y').

    Returns:
        DataFrame: Historical stock data as a DataFrame.
    """
    try:
        symbol = symbol.replace(".", "-")
        return yf.Ticker(symbol).history(period)
    except Exception as e:
        logging.error(
            f"Failed to fetch historical data for {symbol} over {period}: {e}"
        )


@cached_with_force_update()
def info(symbol):
    """
    Fetches financial information for a given stock symbol.

    Parameters:
        symbol (str): The stock symbol.

    Returns:
        dict: A dictionary containing various pieces of financial information about the stock.
    """
    try:
        symbol = symbol.replace(".", "-")
        return yf.Ticker(symbol).info
    except Exception as e:
        logging.error(f"Failed to fetch info for {symbol}: {e}")


@cached_with_force_update()
def annual_financials(symbol):
    """
    Fetches annual financial data for a given stock symbol.

    Args:
        symbol (str): The ticker symbol of the stock.

    Returns:
        DataFrame: Annual financial data.

    Raises:
        ValueError: If an invalid symbol is provided or data cannot be retrieved.
    """
    try:
        symbol = symbol.replace(".", "-")
        data = yf.Ticker(symbol).financials
        if data.empty:
            logger.warning(f"No financial data found for {symbol}.")
        return data
    except Exception as e:
        logger.error(f"Failed to fetch annual financials for {symbol}: {str(e)}")


@cached_with_force_update()
def annual_balance_sheet(symbol):
    """
    Fetches annual balance sheet data for a given stock symbol.

    Args:
        symbol (str): The ticker symbol of the stock.

    Returns:
        DataFrame: Annual balance sheet data.

    Raises:
        ValueError: If an invalid symbol is provided or data cannot be retrieved.
    """
    try:
        symbol = symbol.replace(".", "-")
        data = yf.Ticker(symbol).balance_sheet
        if data.empty:
            logger.warning(f"No balance sheet data found for {symbol}.")
        return data
    except Exception as e:
        logger.error(f"Failed to fetch annual balance sheet for {symbol}: {str(e)}")


@cached_with_force_update()
def quarterly_financials(symbol):
    """
    Fetches quarterly financial data for a given stock symbol.

    Args:
        symbol (str): The ticker symbol of the stock.

    Returns:
        DataFrame: Quarterly financial data.

    Raises:
        ValueError: If an invalid symbol is provided or data cannot be retrieved.
    """
    try:
        symbol = symbol.replace(".", "-")
        data = yf.Ticker(symbol).quarterly_financials
        if data.empty:
            logger.warning(f"No quarterly financial data found for {symbol}.")
        return data
    except Exception as e:
        logger.error(f"Failed to fetch quarterly financials for {symbol}: {str(e)}")


@cached_with_force_update()
def quarterly_balance_sheet(symbol):
    """
    Fetches quarterly balance sheet data for a given stock symbol.

    Args:
        symbol (str): The ticker symbol of the stock.

    Returns:
        DataFrame: Quarterly balance sheet data.

    Raises:
        ValueError: If an invalid symbol is provided or data cannot be retrieved.
    """
    try:
        symbol = symbol.replace(".", "-")
        data = yf.Ticker(symbol).quarterly_balance_sheet
        if data.empty:
            logger.warning(f"No quarterly balance sheet data found for {symbol}.")
        return data
    except Exception as e:
        logger.error(f"Failed to fetch quarterly balance sheet for {symbol}: {str(e)}")
