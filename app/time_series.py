import streamlit as st
import data_fetch
import plotly.graph_objects as go


def get_time_series_data(symbol, time_frame):
    """
    Fetch historical data for a given stock symbol over a specified time frame.

    Parameters:
        symbol (str): The stock symbol.
        time_frame (str): Time frame for historical data, e.g., '1mo', '1y'.

    Returns:
        pandas.DataFrame: Historical stock data.
    """
    try:
        data = data_fetch.history(symbol, time_frame)
        if data.empty:
            raise ValueError(
                f"No data returned for {symbol} with timeframe {time_frame}."
            )
        return data
    except Exception as e:
        st.error(f"Failed to fetch data for {symbol}: {str(e)}")
        return None


def plot_time_series(all_data, time_series, selected_stocks):
    """
    Plot the time series data using Plotly for the selected stocks.

    Parameters:
        all_data (dict): A dictionary of pandas DataFrames indexed by stock symbol.
        time_series (str): Column name to plot, e.g., 'Close'.
        selected_stocks (list): List of selected stock symbols.
    """
    traces = []
    if len(selected_stocks) == 1:
        data = all_data[selected_stocks[0]]
        traces.append(
            go.Scatter(
                x=data.index,
                y=data[time_series],
                name="",
                mode="lines",
                hovertemplate="Close: %{customdata[0]:.2f}<br>"
                + "Open: %{customdata[1]:.2f}<br>"
                + "High: %{customdata[2]:.2f}<br>"
                + "Low: %{customdata[3]:.2f}<br>"
                + "Volume: %{customdata[4]:.0f}",
                customdata=list(
                    zip(
                        data["Close"],
                        data["Open"],
                        data["High"],
                        data["Low"],
                        data["Volume"],
                    )
                ),
            )
        )
    else:
        for stock, data in all_data.items():
            traces.append(
                go.Scatter(
                    x=data.index,
                    y=data[time_series],
                    mode="lines",
                    name=f"{stock}",
                )
            )

    if not traces:
        st.warning("No data available to plot.")
        return

    fig = go.Figure(traces)
    fig.update_layout(
        title=f"{time_series.capitalize()} Over Time",
        xaxis_title="Date",
        yaxis_title=time_series.capitalize(),
        template="plotly_dark",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)


def fetch_time_series_data_and_plot(selected_stocks, time_series, time_frame):
    """
    Main function to fetch data and trigger plotting for selected stocks.

    Parameters:
        selected_stocks (list): Stock symbols to fetch.
        time_series (str): The data type to plot, e.g., 'Close'.
        time_frame (str): The period over which to fetch the data.
    """
    if not selected_stocks:
        st.warning("Please select at least one stock to proceed.")
        return

    time_series_data = {}
    for stock in selected_stocks:
        data = get_time_series_data(stock, time_frame)
        if data is not None:
            time_series_data[stock] = data

    if time_series_data:
        plot_time_series(time_series_data, time_series, selected_stocks)
    else:
        st.error("Failed to retrieve data for plotting.")
