import xlsx from "node-xlsx";
import { Hotel } from "./daten/hotels";
import { BewertungVereinheitlicht } from "./bewertung-vereinheitlicht";

const path = require('path');
const fs = require('fs');

const kopfzeile = [
  'Skala von',
  'Skala bis',
  'Numerischer Wert',
  'Text Titel',
  'Text allgemein',
  'Text positiv',
  'Text negativ',
  'Reise Monat',
  'Reise Gruppe',
  'Reise Dauer',
  'Reise Absicht',
  'Autor Altersgruppe',
  'Autor Nationalität',
];


const inExcelFormat = (bewertung: BewertungVereinheitlicht): string[] => ([
  bewertung.skala.von,
  bewertung.skala.bis,
  bewertung.numerischerWert,
  bewertung.texte.titel,
  bewertung.texte.allgemein,
  bewertung.texte.positiv,
  bewertung.texte.negativ,
  bewertung.reiseInfos.monat,
  bewertung.reiseInfos.gruppe,
  bewertung.reiseInfos.dauer,
  bewertung.reiseInfos.absicht,
  bewertung.autorInfos.altersGruppe,
  bewertung.autorInfos.nationaltaet,
])

export async function bewertungenExportieren(
  bewertungen: BewertungVereinheitlicht[],
  hotel: Hotel,
) {
  const exportDatum = new Date().toISOString();

  const rootPfad = path.resolve(__dirname, '..');
  const exportPfad = `${rootPfad}/excel-dateien/${hotel.name}/${hotel.platform}/${exportDatum}`;
  const dateiName = 'scraper-ergebnis.xlsx';
  const dateiPfad = `${exportPfad}/${dateiName}`;

  const buffer = xlsx.build([{
    name: "Bewertungen",
    data: [
      kopfzeile,
      ...bewertungen.map(inExcelFormat),
    ],
    options: {
      "!cols": Array(bewertungen.keys()).map(() => ({
        wch: 60
      }))
    }
  }]);

  fs.mkdirSync(exportPfad, {
    recursive: true
  });
  fs.writeFileSync(dateiPfad, buffer, {
    /* flag 'wx' wird benutzt, um neue Dateien zu erstellen */
    flag: 'wx'
  });

  return {
    dateiPfad
  }
}
