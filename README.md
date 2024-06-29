# S&P 500 Stock Dashboard

## Overview

The S&P 500 Stock Dashboard is an interactive web application designed to provide in-depth analytics and real-time data
visualization for stocks within the S&P 500 index. Built with Streamlit, this dashboard offers a sector-based view to
explore financial metrics, key ratios, quarterly financials, and historical stock performance.

## Features

- **Real-Time Data Updates**: Utilizes background threading to periodically update data without user interaction.
- **Sector-Based Filtering**: Allows users to view stocks by specific sectors and analyze market trends within these
  sectors.
- **Interactive Time Series Visualization**: Plots stock prices over time and explores different metrics like Open,
  High, Low, Close, and Volume.
- **Detailed Financial Metrics**: Includes key financial ratios, quarterly statistics, and performance metrics.
- **Customizable Views**: Enables users to select specific columns to display and configure pagination for handling
  large datasets efficiently.

## Installation

To run the S&P 500 Stock Dashboard on your local machine, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/Habeeb-MD/stock-dashboard.git
    cd stock-dashboard
    ```

2. **Create a virtual environment**:
    ```bash
    sudo apt install python3-venv
    python3 -m venv app_env
    source app_env/bin/activate
    ```

3. **Install the required Python packages**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Create and configure the secrets file**:
    ```bash
    mkdir .streamlit
    cp secrets.toml .streamlit/secrets.toml
    ```
    - Edit `.streamlit/secrets.toml` to set the configuration details like password, environment, and count of stocks
      for which data needs to be cached.

5. **Run the Streamlit application**:
    ```bash
    streamlit run app/app_stock_dashboard.py
    ```
    - Wait for the cache update to finish. You can check the status in the terminal.
    - Navigate to `http://localhost:8501` in your web browser to view the application.

## Usage

Upon launching the dashboard, select a sector from the dropdown menu to view corresponding stocks. Use the pagination
controls to navigate through different pages of stock data. Customize the data you wish to view using the column
selector. Additional features include:

- Fetching and plotting time series data for selected stocks.
- Displaying financial ratios and quarterly statistics for deeper analysis.
- Calculating and visualizing returns over specified time periods.

## Technologies Used

- **Python**: Primary programming language.
- **Streamlit**: App framework used for building the dashboard.
- **Pandas**: Data manipulation and analysis.
- **Plotly**: Advanced interactive plotting library.

## Acknowledgments

- Special thanks to the Streamlit team for their amazing framework.
- Data provided by Yahoo Finance API.
