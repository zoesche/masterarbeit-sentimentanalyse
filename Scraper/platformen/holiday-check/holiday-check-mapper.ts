import {HolidayCheckBewertung} from "./holiday-check-bewertung";
import {BewertungVereinheitlicht} from "../../bewertung-vereinheitlicht";
import {leerZeichenEntfernen, zahlFormatieren} from "../../bereinigen";


const holidayCheckReiseGruppen: Record<string, BewertungVereinheitlicht['reiseInfos']['gruppe']> = {
  'Verreist als Paar': 'paar',
  'Verreist als Freunde': 'gruppe',
  'Verreist als Familie': 'familie',
  'Alleinreisend': 'alleinreisend',
};

export const holidayCheckMapper = (holidayCheckBewertung: HolidayCheckBewertung): BewertungVereinheitlicht => {
  return {
    skala: {
      von: '1',
        bis: zahlFormatieren(holidayCheckBewertung.sterneInsgesamt),
    },
    numerischerWert: zahlFormatieren(holidayCheckBewertung.sterneGegeben),
      texte: {
    titel: leerZeichenEntfernen(holidayCheckBewertung.titel),
      allgemein: leerZeichenEntfernen(holidayCheckBewertung.bewertungsText)
  },
    reiseInfos: {
      monat: leerZeichenEntfernen(holidayCheckBewertung.reiseDatum),
        gruppe: holidayCheckReiseGruppen[leerZeichenEntfernen(holidayCheckBewertung.reiseGruppe)],
        dauer: leerZeichenEntfernen(holidayCheckBewertung.reiseDauer),
        absicht: leerZeichenEntfernen(holidayCheckBewertung.urlaubsAbsicht),
    },
    autorInfos: {
      altersGruppe: leerZeichenEntfernen(holidayCheckBewertung.altersGruppe),
    }
  }
};
