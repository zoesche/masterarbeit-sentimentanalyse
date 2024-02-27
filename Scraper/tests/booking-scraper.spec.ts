import { test } from '@playwright/test';

/* Paket importieren, um Excel zu exportieren */
import {bookingScrapen} from "../platformen/booking/booking-scraper";
import {hotels} from "../daten/hotels";
import {bewertungenExportieren} from "../export";
import {BookingBewertung} from "../platformen/booking/booking-bewertung";
import {bookingMapper} from "../platformen/booking/booking-mapper";

const zehnMinuten = 10 * 60 * 1000;
test.setTimeout(zehnMinuten);

const bookingHotels = hotels.filter(hotel=>hotel.platform==='booking');

for (const hotel of bookingHotels) {
  test.describe('Booking Scraper', () => {
    const bewertungen: BookingBewertung[] = [];

    test.afterAll('Bewertungen exportieren', async () => {
      console.log('Scraper beendet.');
      console.log('Bewertungen exportieren…');
      const bewertungenVereinheitlicht = bewertungen.map(bookingMapper);
      const { dateiPfad } = await bewertungenExportieren(bewertungenVereinheitlicht, hotel);
      console.log(`${bewertungen.length} Bewertungen wurden in Datei "${dateiPfad}" exportiert`);
    });

    test(`Bewertungen für "${hotel.name}" auslesen`, async ({ page }) => {
      await bookingScrapen(page, hotel, bewertungen);
    });
  })
}
