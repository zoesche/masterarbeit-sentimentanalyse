export type BewertungVereinheitlicht = {
  skala: {
    von: string;
    bis: string;
  };
  numerischerWert: string;
  texte: {
    titel: string;
    allgemein?: string;
    positiv?: string;
    negativ?: string;
  };
  reiseInfos: {
    monat: string;
    gruppe: 'gruppe' | 'paar' | 'alleinreisend' | 'familie';
    dauer?: string;
    absicht?: string;
  };
  autorInfos: {
    nationaltaet?: string;
    altersGruppe?: string;
  };
}
