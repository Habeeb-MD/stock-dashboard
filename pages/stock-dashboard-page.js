// @ts-check
import { expect } from '@playwright/test';

/**
 * Page Object Model for the Stock Dashboard page
 */
export class StockDashboardPage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page;
    this.container = this.getContainer();
    
    // Locators for page elements
    this.dashboardHeader = this.container.locator('[id="stock-dashboard-s-p500"]');
    this.industryDataHeader = this.container.locator('[id="industry-data"]');
    this.sectorFilterInput = this.container.locator('input[aria-label="Selected S&P 500 Index. Filter by Sector"]');
    this.tableHeadersLocator = this.container.locator('[role="columnheader"]');
    this.stockSymbolCells = this.container.locator('[data-testid^="glide-cell-0-"]');
    this.companyNameCells = this.container.locator('[data-testid^="glide-cell-1-"]');
  }

  /**
   * Returns the appropriate container based on URL
   */
  getContainer() {
    return this.page.url().includes('8501') ? 
      this.page.locator('body') : 
      this.page.frameLocator('[title="streamlitApp"]')
  }

  /**
   * Navigate to the dashboard page
   */
  async goto() {
    await this.page.goto('/');
  }

  /**
   * Wait for the application to fully load
   * @param {number} timeout - Maximum time to wait in milliseconds
   */
  async waitForAppToLoad(timeout = 3 * 60 * 1000) {
    // Wait for the dashboard header to be visible
    await this.dashboardHeader.waitFor({ timeout });
    
    // Get the page text to check if app is still starting
    const bodyText = await this.container.owner().allInnerTexts() || '';
    
    // Reload and retry if app is still starting
    if (bodyText.includes("App is starting") || bodyText.includes("Background task started")) {
      await this.page.reload();
      await this.waitForAppToLoad(timeout);
      return;
    }
    
    // Wait for Industry Data to be visible
    await this.industryDataHeader.waitFor({ timeout: 10 * 1000 });
    await expect(this.industryDataHeader).toContainText('Industry Data');
    await expect(this.tableHeadersLocator.first()).toContainText('Symbol');
  }

  /**
   * Filter data by a specific sector
   * @param {string} sectorName - The name of the sector to filter by
   */
  async filterBySector(sectorName) {
    await this.sectorFilterInput.click();
    await this.container.locator('li[role="option"]').filter({ hasText: sectorName }).click();
    
    // Wait for the table to update after filtering
    await this.page.waitForTimeout(1000);
  }

  /**
   * Get all table header texts
   * @returns {Promise<string[]>} Array of header texts
   */
  async getTableHeaders() {
    const headers = [];
    const count = await this.tableHeadersLocator.count();
    
    for (let i = 0; i < count; i++) {
      const text = await this.tableHeadersLocator.nth(i).textContent();
      if (text) headers.push(text.trim());
    }
    
    return headers;
  }

  /**
   * Get all stock symbol texts from the table
   * @returns {Promise<string[]>} Array of stock symbols
   */
  async getStockSymbols() {
    const symbols = [];
    const count = await this.stockSymbolCells.count();
    
    for (let i = 0; i < count; i++) {
      const text = await this.stockSymbolCells.nth(i).textContent();
      if (text) symbols.push(text.trim());
    }
    
    return symbols;
  }

  /**
   * Get all company name texts from the table
   * @returns {Promise<string[]>} Array of company names
   */
  async getCompanyNames() {
    const names = [];
    const count = await this.companyNameCells.count();
    
    for (let i = 0; i < count; i++) {
      const text = await this.companyNameCells.nth(i).textContent();
      if (text) names.push(text.trim());
    }
    
    return names;
  }

  /**
   * Returns the company name cells locator
   * @returns {import('@playwright/test').Locator}
   */
  getCompanyNameCells() {
    return this.companyNameCells;
  }
}