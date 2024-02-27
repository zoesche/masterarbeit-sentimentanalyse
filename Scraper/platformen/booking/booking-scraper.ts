import {Locator, Page, test} from "@playwright/test";
import {Hotel} from "../../daten/hotels";
import {BookingBewertung} from "./booking-bewertung";

/* Cookies akzeptieren: Lokalisierung nur durch ID möglich */
async function cookiesAkzeptieren(page: Page) {
  await page.getByRole('button', {
    name: 'Akzeptieren'
  }).click();
}

async function bewertungenGeladen(page: Page) {
  /*
   * Auf das erste Listenelement mit dem Review Block für bis zu 10 Sekunden warten.
   */
  await page.locator('li:first-child .c-review-block').waitFor({
    timeout: 10000
  });

}

/* "Alle Bewertungen lesen" klicken */
async function bewertungenModalOeffnen(page: Page) {
  const bewertungenButton = page.getByRole('button', {
    name: 'Alle Bewertungen lesen'
  }).first();
  await bewertungenButton.click();

  test.expect(page.locator('h3:text("Gästebewertungen")')).toBeVisible();
}

async function seiteOeffnen(page: Page, seitenNummer: number) {
  let aktuelleSeiteButton: Locator = page.locator('.bui-pagination__item--active');
  let aktuelleSeite: number;

  while ((aktuelleSeite = parseInt(await aktuelleSeiteButton.textContent())) < seitenNummer) {
    await (await weiterButtonFinden(page)).click();
    await bewertungenGeladen(page);
    console.log(`Seite ${aktuelleSeite} geöffnet`);
  }
}

async function findeOptionalesElement(locator: Locator) {
  const count = await locator.count();
  if (count === 0) {
    return undefined;
  }

  return locator;
}

/*
 * Findet den Button, der zur nächsten Seite an Bewertungen führt.
 */
async function weiterButtonFinden(page: Page) {
  return findeOptionalesElement(page.getByRole('link', { name: /nächste seite/i }))
}

async function aktuelleSeiteAuslesen(page: Page, bewertungen: BookingBewertung[]) {
  const reviewBlocks = await page.locator('.c-review-block').all();

  for (const reviewBlock of reviewBlocks) {
    console.log(`Bewertung #${bewertungen.length + 1} auslesen…`);
    try {
      const bewertung = await bewertungAuslesen(reviewBlock);
      bewertungen.push(bewertung);
    } catch (error) {
      console.log('Konnte Bewertung nicht auslesen. Überspringe', error);
    }
  }
}

/* "Bewertungen auslesen" Funktion */
async function bewertungenAuslesen(page: Page, bewertungen: BookingBewertung[], startSeite = 1) {
  let weiterButton: Locator | undefined;
  let seitenNummer = startSeite;

  await bewertungenGeladen(page);

  while (weiterButton = await weiterButtonFinden(page)) {
    await aktuelleSeiteAuslesen(page, bewertungen);
    await weiterButton.click();
    seitenNummer++;
    console.log(`Weiter zu Seite ${seitenNummer}…`);
    await bewertungenGeladen(page);
    console.log(`Seite ${seitenNummer} geladen`);
  }
  await aktuelleSeiteAuslesen(page, bewertungen);
}

/*
 * Klickt auf einen Link "Übersetzung anzeigen", wenn vorhanden
 */
async function uebersetzenWennMoeglich(reviewBlock: Locator) {
  const uebersetzenLink = await findeOptionalesElement(
    reviewBlock.locator(':text("Übersetzung anzeigen")')
  );

  if (uebersetzenLink) {
    await uebersetzenLink.click();
    await reviewBlock.getByRole('link', { name: 'Original anzeigen' }).waitFor({
      state: 'visible'
    });
  }
}

/*
 * Überprüft, ob ein Element eine Klasse hat.
 */
async function hatIcon(reviewRow: Locator, iconKlasse: string) {
  const iconMitKlasse = await findeOptionalesElement(reviewRow.locator(`svg.${iconKlasse}`))
  return iconMitKlasse !== undefined;
}

async function bewertungAuslesen(reviewBlock: Locator): Promise<BookingBewertung> {
  const zensurNachricht = await findeOptionalesElement(
    reviewBlock.locator(':text("Diese Bewertung wird nicht angezeigt, weil sie nicht unseren Richtlinien entspricht.")')
  );

  if(zensurNachricht) {
    return Promise.reject('Bewertung zensiert')
  }

  const name = (await reviewBlock.locator('.bui-avatar-block__title').textContent())!;
  console.log(`Bewertung von ${name}`);

  await uebersetzenWennMoeglich(reviewBlock);

  const kurzBewertung = (await reviewBlock.getByRole('heading', {
    level: 3,
  }).textContent())!;

  const punkteGegeben = (await reviewBlock.locator('.bui-review-score__badge').textContent())!;
  const punkteInsgesamt = '10';

  const reiseInfos = (await reviewBlock.locator('.c-review-block__row ~ .c-review-block__stay-date').textContent())!;
  const [reiseDauer, reiseDatum] = reiseInfos.split('·');
  const reiseGruppe = (await reviewBlock.locator('.review-panel-wide__traveller_type').textContent())!;

  const reviewRows = await reviewBlock.locator('.c-review__row:not(:has-text("Übersetzung anzeigen"))').all();

  const nationalitaetElement = await findeOptionalesElement(reviewBlock.locator('.bui-avatar-block__subtitle:has(.bui-avatar-block__flag)'));
  let nationalitaet = await nationalitaetElement?.textContent();


  let bewertungPositiv: string | null = null;
  let bewertungNegativ: string | null = null;

  for await (const reviewRow of reviewRows) {
    /**
     * Bei übersetzten Bewertungen gibt es zwei Elemente ".c-review__body":
     * - der orginale Text wird versteckt
     * - der übersetzte Text ist sichtbar
     */
    const bewertungsTextElement = reviewRow.locator('.c-review__body:visible');
    const istPositiv = await hatIcon(reviewRow, "-iconset-review_great");
    const istNegativ = await hatIcon(reviewRow, "-iconset-review_poor");
    const bewertungsText = (await bewertungsTextElement.textContent())!;

    if (istPositiv) {
      bewertungPositiv = bewertungsText;
    } else if (istNegativ) {
      bewertungNegativ = bewertungsText;
    }
  }

  return {
    punkteGegeben,
    punkteInsgesamt,
    kurzBewertung,
    bewertungPositiv,
    bewertungNegativ,
    reiseDatum,
    reiseDauer,
    reiseGruppe,
    nationalitaet,
  }
}

export async function bookingScrapen(page: Page, hotel: Hotel, bewertungen: BookingBewertung[]) {
  try {
    /* Cookies leeren, damit akzeptieren button am Anfang erscheint und geclickt werden kann */
    console.log(`Website ${hotel.website} öffnen…`);
    await page.goto(hotel.website);
    console.log('Website geöffnet');

    console.log('Cookie akzeptieren…');
    await cookiesAkzeptieren(page);
    console.log('Cookie akzeptiert');

    /* Tab "Bewertungen" wird geöffnet */
    console.log('Tab "Bewertungen" öffnen…');
    await bewertungenModalOeffnen(page);
    console.log('Tab geöffnet');

    if (hotel.starten_bei_seite) {
      console.log(`Bei Seite ${hotel.starten_bei_seite} beginnen`);
      await seiteOeffnen(page, hotel.starten_bei_seite);
    }

    /* Bewertungen für erste Seite lesen */
    console.log('Bewertungen auslesen…');
    await bewertungenAuslesen(page, bewertungen, hotel.starten_bei_seite);
    console.log(`${bewertungen.length} Bewertungen wurden ausgelesen`);
  } catch (error) {
    console.log('Fehler beim scrapen', error);
  }

  return bewertungen;
}
