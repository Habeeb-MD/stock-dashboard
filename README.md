# S&P 500 Stock Dashboard

## Overview

The S&P 500 Stock Dashboard is an interactive web application designed to provide in-depth analytics and real-time data
visualization for stocks within the S&P 500 index. Built with Streamlit, this dashboard offers a sector-based view to
explore financial metrics, key ratios, quarterly financials, and historical stock performance.

## Features

- **Real-Time Data Updates**: Leveraging background threading to periodically update data without user interaction.
- **Sector-Based Filtering**: Users can view stocks by specific sectors and analyze the market trends within these
  sectors.
- **Interactive Time Series Visualization**: Plot stock prices over time and explore different metrics like Open, High,
  Low, Close, and Volume.
- **Detailed Financial Metrics**: Includes key financial ratios, quarterly statistics, and performance metrics.
- **Customizable Views**: Users can select specific columns to display and configure pagination to handle large datasets
  efficiently.

## Installation

To run the S&P 500 Stock Dashboard on your local machine, follow these steps:

- Clone the repository:
   ```bash
  git clone https://github.com/Habeeb-MD/stock-dashboard.git
  cd stock-dashboard
   ```    
- Install the required Python packages:
  ```bash
  pip install -r requirements.txt
  ```    
- Run the Streamlit application:
  ```bash
  streamlit run app_stock_dashboard.py
  ```    

Navigate to `http://localhost:8501` in your web browser to view the application.

## Usage

Upon launching the dashboard, select a sector from the dropdown menu to view corresponding stocks. Use the pagination
controls to navigate through different pages of stock data. Customize the data you wish to view using the column
selector. Additional features include:

- Fetch and plot time series data for selected stocks.
- Display financial ratios and quarterly statistics for deeper analysis.
- Calculate and visualize returns over specified time periods.

## Technologies Used

- **Python**: Primary programming language.
- **Streamlit**: App framework used for building the dashboard.
- **Pandas**: Data manipulation and analysis.
- **Plotly**: Advanced interactive plotting library.

## Acknowledgments

- Special thanks to the Streamlit team for their amazing framework.
- Data provided by Yahoo Finance API.