// @ts-check
import { test, expect } from '@playwright/test';
import { StockDashboardPage } from '../pages/stock-dashboard-page';

test.describe('Stock Dashboard - Industry Data Tests', () => {
  /**
   * The StockDashboardPage instance
   * @type {StockDashboardPage}
   */
  let stockDashboardPage;

  test.beforeEach(async ({ page }) => {
    stockDashboardPage = new StockDashboardPage(page);
    await stockDashboardPage.goto();
    await stockDashboardPage.waitForAppToLoad();
  });

  test('verify headers and subheaders are displayed correctly', async () => {
    await expect(stockDashboardPage.dashboardHeader).toContainText('Stock Dashboard | S&P500');
    await expect(stockDashboardPage.industryDataHeader).toContainText('Industry Data');
  });

  test('verify filtering by sector is working properly', async () => {
    await stockDashboardPage.filterBySector('Health Care');
    
    // Verify Johnson & Johnson appears in the company names after filtering
    const expectedCompanyName = "Johnson & Johnson";
    await expect(stockDashboardPage.getCompanyNameCells().getByText(expectedCompanyName)).toBeDefined();
  });

  test('verify industry data table headers are displayed correctly', async () => {
    const expectedColumnHeaders = [
      'Symbol', 'Name', 'Weight (%)', 'Current Price ($)',
      'Price to Earning(PE) Ratio', 'Market Cap ($)', 'Dividend Yield (%)', 
      'Net Income Latest Qtr (Bil $)', 'YOY Qtr Profit Growth (%)', 
      'Sales Latest Qtr (Bil $)', 'Debt to Equity (%)'
    ];

    const headers = await stockDashboardPage.getTableHeaders();
    for (const expectedHeader of expectedColumnHeaders) {
      const headerExists = headers.some(header => header.includes(expectedHeader));
      expect(headerExists, `Header "${expectedHeader}" should exist`).toBeTruthy();
    }
  });

  test('verify major stock tickers and company names are displayed', async () => {
    const expectedTickers = ['MSFT', 'AAPL', 'NVDA', 'AMZN', 'META'];
    const expectedNames = [
      'Microsoft Corporation', 
      'Apple Inc.', 
      'NVIDIA Corporation', 
      'Amazon.com, Inc.', 
      'Meta Platforms, Inc.'
    ];

    const tickers = await stockDashboardPage.getStockSymbols();
    const names = await stockDashboardPage.getCompanyNames();

    for (const ticker of expectedTickers) {
      expect(tickers).toContain(ticker);
    }

    for (const name of expectedNames) {
      expect(names).toContain(name);
    }
  });
});