import playwright from 'playwright';
import { URL_DASHBOARD, URL_LOGIN, URL_TOP_PAGE } from './constant';
import { Logger } from './types';

export async function TokyoGasScraper(
  username: string,
  password: string,
  customerNumber: string,
  logger: Logger,
) {

  const browser = await playwright.chromium.launch({
    executablePath: '/usr/bin/chromium-browser',
  });
  const context= await browser.newContext();

  return {
    async login() {
      const page = await context.newPage();

      await page.goto(URL_TOP_PAGE);
      await page.getByRole('link', { name: 'ログイン', exact: false }).first().click();

      await page.waitForURL(URL_LOGIN);
      await page.fill('input#loginId', username);
      await page.fill('input#password', password);
      await page.click('#submit-btn');

      await page.waitForURL(URL_DASHBOARD);

      logger.info(await page.title());
    }
  }
}