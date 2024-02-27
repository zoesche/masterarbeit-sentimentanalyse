import argparse
import os
from enum import Enum

import pandas as pd
from pandas import DataFrame


def data_frame_laden(datei_pfad: str) -> DataFrame:
    data_frame = pd.read_excel(
        os.path.join(os.path.dirname(__file__), datei_pfad)
    )

    # Leere Spalten mit leerem String anstatt nan (not a number) füllen
    data_frame = data_frame.fillna('')

    return data_frame


def data_frame_speichern(data_frame: DataFrame, datei_pfad: str):
    data_frame.to_excel(datei_pfad)


class AnalyseMethode(Enum):
    nltk = 'nltk'
    gervader = 'gervader'
    textblob = 'textblob'

    def __str__(self):
        return self.value


bevorzugte_analyse_methode = AnalyseMethode.gervader


class Spalten(Enum):
    portal = 'Portal'
    skala_von = 'Skala von'
    skala_bis = 'Skala bis'
    numerischer_wert = 'Numerischer Wert'
    text_titel = 'Text Titel'
    text_allgemein = 'Text allgemein'
    text_positiv = 'Text positiv'
    text_negativ = 'Text negativ'
    reise_monat = 'Reise Monat'
    reise_gruppe = 'Reise Gruppe'
    reise_dauer = 'Reise Dauer'
    reise_absicht = 'Reise Absicht'
    autor_altersgruppe = 'Autor Altersgruppe'
    autor_nationalitaet = 'Autor Nationalität'
    nutzer_score_normiert = 'Nutzerscore normiert'
    score = 'Score'
    diskrepanz = 'Diskrepanz'
    zu_bewertender_text = 'Zu Bewertender Text'
    sortierung = 'Sortierung'

    # https://stackoverflow.com/questions/62277882/python-pandas-sort-dataframe-by-enum-class-values
    def __str__(self):
        return self.value


def datei_pfad_laden():
    parser = argparse.ArgumentParser()
    parser.add_argument("dateiname")
    args, unknown = parser.parse_known_args()

    if not args.dateiname:
        raise Exception("Wähle bitte eine Datei aus")

    return args.dateiname


monate = {
    'Januar': 1,
    'Februar': 2,
    'März': 3,
    'April': 4,
    'Mai': 5,
    'Juni': 6,
    'Juli': 7,
    'August': 8,
    'September': 9,
    'Oktober': 10,
    'November': 11,
    'Dezember': 12,
    'Unbekannt': -1
}


def monats_name(monat_als_zahl):
    return [k for k, v in monate.items() if v == monat_als_zahl][0]
