import {Hotel} from "../../daten/hotels";

/* Wenn eine neue Seite lädt, muss abgewartet werden, bis diese fertig geladen hat */
import {Locator, Page} from "@playwright/test";
import {bewertungenExportieren} from "../../export";
import {HolidayCheckBewertung} from "./holiday-check-bewertung";
import {holidayCheckMapper} from "./holiday-check-mapper";

async function seiteGeladen(page: Page) {
  await page.waitForLoadState();
}

/* Cookie iframe akzeptieren */
async function cookiesAkzeptieren(page: Page) {
  const akzeptierenButton = page.frameLocator('iframe[title="SP Consent Message"]').getByLabel('Akzeptieren');
  await akzeptierenButton.click();
}

/* Integrierten Tab "Bwertungen" klicken */
async function bewertungenTabOeffnen(page: Page) {
  const horizontaleTabBar = page.locator('#HotelNavBarList');
  const bewertungenTab = horizontaleTabBar.getByText('Bewertungen');
  await bewertungenTab.click();
  await seiteGeladen(page);
}

async function seiteOeffnen(page: Page, seitenNummer: number) {
  await page.goto(`${page.url()}/-/p/${seitenNummer}`)
  console.log(`Seite ${seitenNummer} geöffnet`);
}

/* Funktion "Bewertungen auslesen" */
async function bewertungenAuslesen(page: Page, bewertungen: HolidayCheckBewertung[], startSeite = 1) {
  let weiterButton;
  let seitenNummer = startSeite;
  while (weiterButton = weiterButtonFinden(page)) {
    await aktuelleSeiteAuslesen(page, bewertungen);
    await weiterButton.click();
    seitenNummer++;
    console.log(`Weiter zu Seite ${seitenNummer}…`);
    await seiteGeladen(page);
    console.log(`Seite ${seitenNummer} geladen`);
  }
  await aktuelleSeiteAuslesen(page, bewertungen);

}

/* Funktion "Pagination eine Seite weiter blättern" */
function weiterButtonFinden(page: Page) {
  return page.locator('.prev-next:right-of(.active-page)');
}

async function aktuelleSeiteAuslesen(page: Page, bewertungen: HolidayCheckBewertung[]) {
  const hotelReviewItems = await page.locator('.hotel-review-item').all();

  for (const hotelReviewItem of hotelReviewItems) {
    console.log(`Bewertung #${bewertungen.length + 1} auslesen…`);
    try {
      const bewertung = await bewertungAuslesen(hotelReviewItem);
      bewertungen.push(bewertung);
    } catch (error) {
      console.log('Konnte Bewertung nicht auslesen. Überspringe', error);
    }
  }
}

/*
TODO:
Mehr auslesen:
- Altersgruppe
 */
async function bewertungAuslesen(hotelReviewItem: Locator): Promise<HolidayCheckBewertung> {
  const name = (await hotelReviewItem.locator('.css-1itv5e3').textContent())!;
  console.log(`Bewertung von ${name}`);
  /*
  Regulärer Ausdruck, um Altersgruppe zu finden. Beispiel: Maik (41-55)
  / = Anfang und Ende von regulärem Ausdruck
  .* = Beliebiger Text
  \( = (
  \) = )
  () = Gruppe, die gefunden werden soll
  -> Alles finden, was in runden Klammern steht
  */
  const altersGruppeFormat = /.*\((.*)\)/;
  /*
  .match gibt …
   */
  const altersGruppeTreffer = name.match(altersGruppeFormat);
  const altersGruppe = altersGruppeTreffer?.[1] ?? null;

  await hotelReviewItem.getByRole('button', {
    name: 'Bewertung lesen'
  }).click();

  const hotelReviewHeader = hotelReviewItem.locator('.hotel-review-header');

  /*
  Jede Bewertung besteht aus mindestens dem Titel.
  */
  const titel = (await hotelReviewItem.locator('.css-1pesbvn').textContent())!;

  /*
  Der Text wird in den meisten Fällen in einem Element mit der testid "GeneralContent" hinterlegt.
  Das Element wird gesucht und falls es existiert wird der Text ausgelesen.
   */
  const bewertungsTextElement = hotelReviewItem.locator('data-testid=GeneralContent');
  const bewertungsText = await bewertungsTextElement.isVisible() ? await bewertungsTextElement.textContent() : null;


  /*
  Alternativ kann es einen Text unter der Kategorie "Allgemein" geben. Dieser wird verwendet, falls "bewertungsText" leer ist.
   */
  const bewertungsTextKategorieAllgemeinElement = hotelReviewItem.locator('.css-1lr4zai:near(:text("Allgemein"))');
  const bewertungsTextKategorieAllgemein = await bewertungsTextKategorieAllgemeinElement.isVisible() ? await bewertungsTextKategorieAllgemeinElement.textContent() : null;

  /*
  Regulärer Ausdruck, um Sternebewertung zu finden. Beispiel: 4,5 / 6
  / = Anfang und Ende von regulärem Ausdruck
  [0-6] = Zahl von 0 bis 6
  \s = leerzeichen
  \/ = slash
  */
  const sterneBewertungFormat = /[0-6],[0-9]\s\/\s6/;
  const sterneBewertungInhalt = await hotelReviewHeader.getByText(sterneBewertungFormat).textContent();
  const [sterneGegeben, sterneInsgesamt] = sterneBewertungInhalt!.split(' / ');

  /*
  Automatische ID wird verwendet, da keine bessere Identifizierung möglich ist.
  String in mehrere strings unterteilt, um Reisedatum und -Dauer herauszufiltern.
  */
  const reiseInfos = (await hotelReviewHeader.locator('.css-b1qje2').textContent())!;
  const [reiseGruppe, reiseDatum, reiseDauer, urlaubsAbsicht] = reiseInfos.split(' • ');

  return {
    sterneGegeben,
    sterneInsgesamt,
    reiseGruppe,
    // Wenn es keinen normalen Text gibt, wird stattdessen der Text aus der Kategorie "Allgemein" benutzt
    bewertungsText: bewertungsText || bewertungsTextKategorieAllgemein,
    titel,
    reiseDatum,
    reiseDauer: reiseDauer ? reiseDauer : null,
    altersGruppe,
    urlaubsAbsicht,
  }
}

export async function holidayCheckHotelScrapen(page: Page, hotel: Hotel) {
  const bewertungen: HolidayCheckBewertung[] = [];

  try {
    /* Cookies leeren, damit akzeptieren button am Anfang erscheint und geklickt werden kann */
    await page.context().clearCookies();

    console.log('Website öffnen…');
    await page.goto(hotel.website);
    console.log('Website geöffnet');

    console.log('Cookie akzeptieren…');
    await cookiesAkzeptieren(page);
    console.log('Cookie akzeptiert');

    /* Tab "Bewertungen" wird geöffnet */
    console.log('Tab "Bewertungen" öffnen…');
    await bewertungenTabOeffnen(page);
    console.log('Tab geöffnet');

    if (hotel.starten_bei_seite) {
      console.log(`Bei Seite ${hotel.starten_bei_seite} beginnen`);
      await seiteOeffnen(page, hotel.starten_bei_seite);

      console.log('Cookie akzeptieren…');
      await cookiesAkzeptieren(page);
      console.log('Cookie akzeptiert');
    }

    /* Bewertungen für erste Seite lesen */
    console.log('Bewertungen auslesen…');
    await bewertungenAuslesen(page, bewertungen);
    console.log(`${bewertungen.length} Bewertungen wurden ausgelesen`);
  } catch (error) {
    console.log('Fehler beim scrapen', error);
  } finally {
    console.log('Scraper beendet.');
    console.log('Bewertungen exportieren…');
    const bewertungenVereinheitlicht = bewertungen.map(holidayCheckMapper);
    const { dateiPfad } = await bewertungenExportieren(bewertungenVereinheitlicht, hotel);
    console.log(`${bewertungen.length} Bewertungen wurden in Datei "${dateiPfad}" exportiert`);
  }
}
