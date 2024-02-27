import { chromium } from 'playwright-extra';

import { hotels } from "../daten/hotels";
import { holidayCheckHotelScrapen } from "../platformen/holiday-check/holiday-check-scraper";

const stealth = require('puppeteer-extra-plugin-stealth')()

chromium.use(stealth);

chromium.launch({ headless: false }).then(async (browser) => {
  await Promise.allSettled(
    hotels
      .filter(hotel => hotel.platform === 'holiday-check')
      .map(async hotel => {
        const page = await browser.newPage();
        await holidayCheckHotelScrapen(page, hotel);
      })
  );

  await browser.close();
})
