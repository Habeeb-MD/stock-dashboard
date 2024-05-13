import streamlit as st
import plotly.graph_objects as go
import data_fetch


def _handle_division(numerator, denominator):
    """
    Safely divides two numbers and handles division by zero.

    Args:
        numerator (float): The numerator in the division.
        denominator (float): The denominator in the division.

    Returns:
        float or None: The result of the division or None if denominator is zero.
    """
    try:
        return numerator / denominator
    except TypeError:
        return None


def _fetch_financial_ratio_for_single_symbol(symbol):
    """
    Fetches and calculates key financial ratios for a given stock symbol using annual and quarterly data.

    Args:
        symbol (str): The stock symbol.

    Returns:
        dict: A dictionary containing calculated financial ratios.
    """
    try:
        annual_financials = data_fetch.annual_financials(symbol).T
        annual_balance_sheet = data_fetch.annual_balance_sheet(symbol).T
        financials = data_fetch.quarterly_financials(symbol).T
        balance_sheet = data_fetch.quarterly_balance_sheet(symbol).T

        if financials.empty or balance_sheet.empty:
            st.warning(f"No data available for {symbol}")
            return {}

        ratios = {
            # Calculate financial ratios
            # https://www.wisesheets.io/roe/MSFT
            "Annual Return on equity %": _handle_division(
                annual_financials["Net Income"],
                annual_balance_sheet["Stockholders Equity"],
            ),
            # https://ycharts.com/companies/MSFT/profit_margin
            "Net Profit Margin": _handle_division(
                financials["Net Income"], financials["Total Revenue"]
            ),
            # https://www.gurufocus.com/term/earning-per-share-diluted/MSFT
            # https://tradingeconomics.com/msft:us:eps
            "EPS": _handle_division(
                financials["Net Income"], financials["Diluted Average Shares"]
            ),
            # https://www.gurufocus.com/term/debt-to-equity/MSFT#:~:text=Microsoft%20(Microsoft)%20Debt%2Dto,2024)
            "Debt to Equity": _handle_division(
                balance_sheet["Total Debt"],
                balance_sheet["Stockholders Equity"],
            ),
        }
        # convert to percentage
        for column in [
            "Annual Return on equity %",
            "Net Profit Margin",
        ]:
            ratios[column] = ratios[column].apply(lambda x: x * 100 if x else None)
        return ratios
    except Exception as e:
        st.error(f"Failed to fetch data for {symbol}: {str(e)}")
        return {}


def fetch_financial_ratios_for_multiple_symbols(symbols):
    """
    Fetches financial ratios for multiple symbols.

    Args:
        symbols (list of str): List of stock symbols.

    Returns:
        dict: A dictionary with symbols as keys and their financial ratios as values.
    """
    data = {
        symbol: _fetch_financial_ratio_for_single_symbol(symbol) for symbol in symbols
    }
    return data


def get_financial_ratios_figure_for_single_metric(metric, stock_data):
    """
    Creates a plotly graph object figure for a single financial metric across multiple stocks.

    Args:
        metric (str): The metric to plot.
        stock_data (dict): Data containing financial ratios for various stocks.

    Returns:
        plotly.graph_objects.Figure: A plotly figure.
    """
    fig = go.Figure()
    for stock, data_dict in stock_data.items():
        fig.add_trace(
            go.Scatter(
                x=data_dict[metric].index,
                y=data_dict[metric],
                mode="lines+markers",
                name=stock,
            )
        )
    fig.update_layout(
        title=f"{metric}",
        xaxis_title="Date",
        yaxis_title=metric,
        template="plotly_white",
        hovermode="x unified",
    )
    return fig


def plot_financial_ratios(stock_data):
    """
    Plots charts for each financial ratio for given stock data.

    Args:
        stock_data (dict): A dictionary containing financial ratios for different stocks.
    """
    financial_ratios = [
        "Annual Return on equity %",
        "Net Profit Margin",
        "EPS",
        "Debt to Equity",
    ]
    charts = [st.columns(2), st.columns(2)]
    for i, metric in enumerate(financial_ratios):
        with charts[i // 2][i % 2]:
            fig = get_financial_ratios_figure_for_single_metric(metric, stock_data)
            st.plotly_chart(fig, use_container_width=True)


def display_financial_ratios(selected_stocks):
    """
    Displays financial ratios comparison across selected stocks.

    Args:
        selected_stocks (list of str): A list of stock symbols to analyze.
    """
    st.subheader("Financial Ratios Comparison Across Stocks")
    stock_data = fetch_financial_ratios_for_multiple_symbols(selected_stocks)
    plot_financial_ratios(stock_data)
