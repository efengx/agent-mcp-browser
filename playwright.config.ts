import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // Look for test files in the "tests" directory, relative to this configuration file.
  testDir: 'tests',

  outputDir: 'output',

  // Run all tests in parallel.
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only in the source code.
  forbidOnly: !!process.env.CI,

  // Retry on CI only.
  retries: process.env.CI ? 2 : 0,

  // Opt out of parallel tests on CI.
  workers: process.env.CI ? 1 : undefined,

  // Reporter to use
  reporter: 'html',

  use: {
    // Base URL to use in actions like `await page.goto('/')`.
    // baseURL: 'http://localhost:3000',

    // Collect trace when retrying the failed test.
    trace: 'on-first-retry',
    ignoreHTTPSErrors: true,
    
    // Populates context with given storage state.
    // storageState: 'config/user.json',
  },
  // Configure projects for major browsers.
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
      },
    },
    {
      name: 'chrome-cdp-macos',
      use: {
        ...devices['Desktop Chrome'],
        // 启用CDP连接到已运行的Chrome实例
        channel: 'chrome',
        launchOptions: {
          args: ['--remote-debugging-port=9222'],
          headless: false
        }
      },
    },
    {
      name: 'remote-browser',
      use: {
        ...devices['Desktop Chrome'],
        // 使用默认配置中的connectOptions连接到远程浏览器
      },
    },
  ],
  // Run your local dev server before starting the tests.
  // webServer: {
  //   command: 'npm run start',
  //   url: 'http://localhost:3000',
  //   reuseExistingServer: !process.env.CI,
  // },
});
