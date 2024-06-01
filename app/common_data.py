import streamlit as st

industry_dataframe_default_cols = [
    "Symbol",
    "Name",
    "Weight",
    "Current Price",
    "Price to Earning",
    "Market Capitalization",
    "Dividend Yield",
    "Net Income Latest Quarter",
    "YOY Quarterly Profit Growth",
    "Sales Latest Quarter",
    "Debt to Equity",
    "YOY Quarterly Sales Growth",
    "Return on Capital Employed",
]

industry_dataframe_all_cols = [
    "Symbol",
    "Name",
    "Weight",
    "Sector",
    "Current Price",
    "Price to Earning",  # Trailing P/E	https://finance.yahoo.com/quote/MSFT/key-statistics
    # PE Ratio(TTM) Earnings per Share(Diluted)
    "Market Capitalization",  # Market Cap https://finance.yahoo.com/quote/MSFT/key-statistics
    "Dividend Yield",  # Trailing Annual Dividend Yield: https://finance.yahoo.com/quote/MSFT/key-statistics
    # This metric calculates the annualized dividend yield based  on the past year's dividend payments.
    "Net Income Latest Quarter",  # Net Income Common Stockholders https://finance.yahoo.com/quote/MSFT/financials
    "YOY Quarterly Profit Growth",  # EPS Growth (Quarterly YoY)  https://finance.yahoo.com/quote/AAPL/key-statistics
    "Sales Latest Quarter",  # Total Revenue https://finance.yahoo.com/quote/AAPL/financials
    "YOY Quarterly Sales Growth",  # Quarterly Revenue Growth (yoy) https://finance.yahoo.com/quote/MSFT/key-statistics
    "Debt to Equity",  # Total Debt/Equity (mrq) https://finance.yahoo.com/quote/MSFT/key-statistics
    "Return on Capital Employed",
]

stock_dataframe_column_config = {
    "Weight": st.column_config.NumberColumn(
        "Weight (%)",
        format="%.2f",
        help="Weight(%) of asset in Index by Market Capitalization",
    ),
    "Price to Earning": st.column_config.NumberColumn(
        "Price to Earning(PE) Ratio",
        format="%.2f",
        help="PE Ratio (TTM)",
    ),
    "Current Price": st.column_config.NumberColumn(
        "Current Price ($)", format="%.2f", help="Current Price now in USD"
    ),
    "Market Capitalization": st.column_config.NumberColumn(
        "Market Cap ($)",
        format="%.2f",
        help="Market Capitalization  in Billions USD",
    ),
    "Dividend Yield": st.column_config.NumberColumn(
        "Dividend Yield (%)",
        format="%.2f",
        help="Annual dividend yield Percentage",
    ),
    "Net Income Latest Quarter": st.column_config.NumberColumn(
        "Net Income Latest Qtr (Bil $)",
        format="%.2f",
        help="Net Income Latest Quarter in Billions USD",
    ),
    "YOY Quarterly Profit Growth": st.column_config.NumberColumn(
        "YOY Qtr Profit Growth (%)",
        format="%.2f",
        help="EPS Growth Percent(Quarterly YoY)",
    ),
    "Sales Latest Quarter": st.column_config.NumberColumn(
        "Sales Latest Qtr (Bil $)",
        format="%.2f",
        help="Total Revenue Latest Quarter in Billions USD",
    ),
    "Debt to Equity": st.column_config.NumberColumn(
        "Debt to Equity (%)",
        format="%.2f",
        help="Total Debt/Equity for Latest Quarter",
    ),
    "YOY Qtr Sales Growth": st.column_config.NumberColumn(
        "Quarterly Sales Growth YoY (%)",
        format="%.2f",
        help="Quarterly Revenue Growth Percent(yoy) ",
    ),
    "Return on Capital Employed": st.column_config.NumberColumn(
        "ROCE %",
        format="%.2f",
        help="Annualized Return on Capital Employed %",
    ),
}

financial_columns = [
    "Basic Average Shares",
    "Basic EPS",
    "Cost Of Revenue",
    "Diluted Average Shares",
    "Diluted EPS",
    "EBIT",
    "EBITDA",
    "Gross Profit",
    "Interest Expense",
    "Interest Expense Non Operating",
    "Interest Income",
    "Interest Income Non Operating",
    "Net Income",
    "Net Income Common Stockholders",
    "Net Income Continuous Operations",
    "Net Income From Continuing And Discontinued Operation",
    "Net Income From Continuing Operation Net Minority Interest",
    "Net Interest Income",
    "Net Non Operating Interest Income Expense",
    "Normalized EBITDA",
    "Normalized Income",
    "Operating Expense",
    "Operating Income",
    "Operating Revenue",
    "Other Income Expense",
    "Other Non Operating Income Expenses",
    "Pretax Income",
    "Reconciled Cost Of Revenue",
    "Reconciled Depreciation",
    "Research And Development",
    "Selling And Marketing Expense",
    "Selling General And Administration",
    "Tax Provision",
    "Tax Rate For Calcs",
    "Total Expenses",
    "Total Operating Income As Reported",
    "Total Revenue",
]
financial_columns_renamed = {
    "Net Income Including Noncontrolling Interests": "Net Income Including Non controlling Interests",
    "Diluted NI Availto Com Stockholders": "Diluted NI Available to Common Stockholders",
}


# all time periods with their Yahoo Finance codes
all_time_periods = {
    "1 Day": "1d",
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "YTD": "ytd",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y",
    "10 Years": "10y",
    "MAX": "max",
}

# Define default time periods with their Yahoo Finance codes
default_time_periods = {
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "YTD": "ytd",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y",
}

# available_time_series for plotting
available_time_series = ["Open", "High", "Low", "Close", "Volume"]

# sidebar menu
menus = [
    "Industry Data",
    "Stock Details",
    "Quarterly Financials",
    "Metrics",
    "Ratios",
    "Returns",
]
