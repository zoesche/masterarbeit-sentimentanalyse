import {BookingBewertung} from "./booking-bewertung";
import {BewertungVereinheitlicht} from "../../bewertung-vereinheitlicht";
import {leerZeichenEntfernen, zahlFormatieren} from "../../bereinigen";

const bookingReiseGruppen: Record<string, BewertungVereinheitlicht['reiseInfos']['gruppe']> = {
  'Paar': 'paar',
  'Gruppe': 'gruppe',
  'Alleinreisende:r': 'alleinreisend',
  'Familie': 'familie'
};

export const bookingMapper = (bookingBewertung: BookingBewertung): BewertungVereinheitlicht => {
  return {
    skala: {
      von: '1',
      bis: zahlFormatieren(bookingBewertung.punkteInsgesamt),
    },
    numerischerWert: zahlFormatieren(bookingBewertung.punkteGegeben),
    texte: {
      titel: leerZeichenEntfernen(bookingBewertung.kurzBewertung),
      positiv: leerZeichenEntfernen(bookingBewertung.bewertungPositiv),
      negativ: leerZeichenEntfernen(bookingBewertung.bewertungNegativ)
    },
    reiseInfos: {
      monat: leerZeichenEntfernen(bookingBewertung.reiseDatum),
      gruppe: bookingReiseGruppen[leerZeichenEntfernen(bookingBewertung.reiseGruppe)],
      dauer: leerZeichenEntfernen(bookingBewertung.reiseDauer),
    },
    autorInfos: {
      nationaltaet: leerZeichenEntfernen(bookingBewertung.nationalitaet),
    }
  }
};
