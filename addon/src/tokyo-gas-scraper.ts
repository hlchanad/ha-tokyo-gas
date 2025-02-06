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
    // executablePath: '/usr/bin/chromium-browser',
    headless: false,
  });
  const context= await browser.newContext();
  const page = await context.newPage();

  async function spyOnGraphqlResponse(key: string) {
    return page.waitForResponse(async response => {
      if (!/graphql$/.test(response.url())) {
        return false;
      }

      const body = await response.json();
      return 'data' in body && 'hourlyElectricityUsage' in body.data;
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
    logger.debug('Submitted ')

    await page.waitForURL(URL_DASHBOARD);
  }

  async function navigateToHourlyElectricityUsage() {
    await page.goto(URL_ELECTRICITY_USAGE);
  }

  return {
    async fetchElectricityUsage(date: string) {
      await login();

      await navigateToHourlyElectricityUsage();

      const responsePromise = spyOnGraphqlResponse('hourlyElectricityUsage');
      await page.getByRole('button', { name: '時間' }).click();
      const response = await responsePromise;
      const body = await response.json() as { data: { hourlyElectricityUsage: any[] }};

      return body.data.hourlyElectricityUsage;
    }
  };
}