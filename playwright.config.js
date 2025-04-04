// @ts-check
import { defineConfig, devices } from '@playwright/test';

/**
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry tests on CI */
  retries: process.env.CI ? 2 : 0,
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [['html'], ['line']],
  
  /* Timeout settings */
  timeout: 5 * 60 * 1000, // Global timeout for tests
  expect: {
    timeout: 10 * 1000, // Default timeout for assertions
  },

  /* Configure projects for different browsers */
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        /* Capture video for visual debugging and analysis */
        video: 'retain-on-failure',
        /* Capture screenshots on test failures */
        screenshot: 'only-on-failure',
        /* Increase timeout for navigation */
        navigationTimeout: 30 * 1000,
        /* Ignore HTTPS errors for self-signed certificates */
        ignoreHTTPSErrors: true,
        /* Viewport size */
        viewport: { width: 1920, height: 1080 },
        /* Trace for debugging */
        trace: 'retain-on-failure',
      },
    },
    
    /* Uncomment these if you need to test in other browsers */
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },
    // {
    //   name: 'mobile-chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
    // {
    //   name: 'mobile-safari',
    //   use: { ...devices['iPhone 12'] },
    // },
  ],
  
  /* Run your local dev server before starting the tests */
  // webServer: {
  //   command: 'npm run start',
  //   url: 'http://127.0.0.1:8501',
  //   reuseExistingServer: !process.env.CI,
  // },

  /* Global setup/teardown hooks */
  // globalSetup: require.resolve('./global-setup'),
  // globalTeardown: require.resolve('./global-teardown'),
  
  /* Use a base URL for easier environment switching */
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:8501',
  },
});