import playwright from 'playwright';
import { URL_DASHBOARD, URL_ELECTRICITY_USAGE, URL_LOGIN, URL_TOP_PAGE } from './constant';
import { Logger } from './types';

export async function TokyoGasScraper(
  username: string,
  password: string,
  customerNumber: string,
  logger: Logger,
) {

  const browser = await playwright.chromium.launch({
    executablePath: '/usr/bin/chromium-browser',
    // headless: false,
  });
  const context= await browser.newContext();
  const page = await context.newPage();

  async function spyOnGraphqlResponse(key: string) {
    return page.waitForResponse(async response => {
      if (!/graphql$/.test(response.url())) {
        return false;
      }

      const body = await response.json();
      return 'data' in body && key in body.data;
    });
  }

  async function login() {
    await page.goto(URL_TOP_PAGE);
    await page.getByRole('link', { name: 'ログイン', exact: false }).first().click();
    logger.debug('Clicked login button');

    await page.waitForURL(URL_LOGIN);
    await page.fill('input#loginId', username);
    await page.fill('input#password', password);
    await page.click('#submit-btn');
    logger.debug('Submitted credentials');

    await page.waitForURL(URL_DASHBOARD);
    logger.debug('Logged in to TokyoGas');
  }

  async function navigateToHourlyElectricityUsage() {
    await page.goto(URL_ELECTRICITY_USAGE);
    logger.debug('Navigated to Electricity Usage Page');
  }

  async function interceptElectricityUsageResponse(date: string) {
    const isHourlyElectricityUsage = (postData: { operationName: string }): postData is {
      operationName: 'HourlyElectricityUsage';
      variables: {
        targetDate: string | null;
      }
    } => postData.operationName === 'HourlyElectricityUsage';

    // intercept request and response
    await page.route(/graphql$/, async (route) => {
      // postData will not be null if it's /graphql
      const postData = JSON.parse(route.request().postData()!) as { operationName: string };

      if (!isHourlyElectricityUsage(postData)) {
        await route.continue();
        return
      }

      postData.variables.targetDate = date;
      await route.continue({ postData });
    })
    const responsePromise = spyOnGraphqlResponse('hourlyElectricityUsage');
    logger.debug('Set interceptor for request and response');

    // clicking 'Hour' trigger the graphql API
    await page.getByRole('button', { name: '時間' }).click();

    // get the intercepted response body
    const response = await responsePromise;
    const body = await response.json() as { data: { hourlyElectricityUsage: any[] }};

    return body.data.hourlyElectricityUsage;
  }

  return {
    async fetchElectricityUsage(date: string) {
      await login();

      await navigateToHourlyElectricityUsage();

      return interceptElectricityUsageResponse(date);
    }
  };
}