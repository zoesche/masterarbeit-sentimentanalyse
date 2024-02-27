# TextBlobDE wird als Classifier importiert
import datetime

from matplotlib.lines import Line2D
from textblob_de import TextBlobDE as TextBlob

# NLTK wird importiert
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import re
import sys
from collections import Counter

# Um deutsche Bewertungstexte zu klassifizieren wird der GerVADER als Werkzeug importiert
from GerVADER.vaderSentimentGER import SentimentIntensityAnalyzer as SentimentIntensityAnalyzerGerman

# Pandas (DataFrame-Umsetzung) & numpy (Normierung) werden importiert
from pandas import DataFrame, Series
import numpy
import matplotlib.pyplot as plt

from typing import List

import os

from gemeinsame_funktionen import data_frame_laden, data_frame_speichern, AnalyseMethode, bevorzugte_analyse_methode, \
    Spalten, datei_pfad_laden, monate, monats_name
from qualitaets_analyse import methoden_vergleichen

# Packages werden aus der NLTK Library heruntergeladen
nltk.download('punkt')
nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('wordnet')

# setting path
sys.path.append('.')

eigene_stop_woerter = {
    "beim",
    "vllt",
    "``",
    ".."
}


def zu_analysierende_spalte_erstellen(bewertung: Series, spalten: List[str]):
    return ' '.join(bewertung[spalten])


# Pandas zum auslesen von Data-Frames (durch Scraper generierte Excel)


# Eine Zahl wird von Skala 1 auf Skala 2 übertragen.
# Z.B. wird eine Punktzahl von Holidaycheck (0 bis 6 Sterne) auf die gleiche Skala wie die Sentiment Scores (-1 bis 1) übertragen
def skala_anpassen(ausgangs_skala_wert, ausgangs_skala_von, ausgangs_skala__bis, ziel_skala_von, ziel_skala_bis):
    return numpy.interp(ausgangs_skala_wert, [ausgangs_skala_von, ausgangs_skala__bis],
                        [ziel_skala_von, ziel_skala_bis])


def spalten_name_fuer_plot(spalte: str):
    if spalte == str(Spalten.autor_nationalitaet):
        return 'Nationalität des oder der Autor:in'
    elif spalte == str(Spalten.autor_altersgruppe):
        return 'Alter des oder der Autor:in'
    else:
        return spalte


# Die Bereinigung mittels Funktionen aus nltk liefert die größten Verbesserungen.
def text_bereinigen(satz: str) -> list[str]:
    stop_woerter = set(stopwords.words('german')).union(eigene_stop_woerter)

    # Tokenisierung
    woerter = word_tokenize(satz, language='german')
    # Kleinschreibung
    woerter = [wort.lower() for wort in woerter]
    # Stopwörter und Satzzeichen entfernen
    woerter = [wort for wort in woerter if wort not in string.punctuation and wort not in stop_woerter]
    # Lemmatisierung
    lemmatizer = WordNetLemmatizer()
    woerter = [lemmatizer.lemmatize(wort) for wort in woerter]

    return woerter


def score_berechnen_mit_methode(zeile: Series, methode: AnalyseMethode) -> float:
    text = zeile[str(Spalten.zu_bewertender_text)]

    if methode == AnalyseMethode.gervader:
        analyse = SentimentIntensityAnalyzerGerman()
        scores = analyse.polarity_scores(text)
        return scores["compound"]
    elif methode == AnalyseMethode.nltk:
        analyse = SentimentIntensityAnalyzer()
        scores = analyse.polarity_scores(text)
        return scores["compound"]
    elif methode == AnalyseMethode.textblob:
        analyse = TextBlob(text)
        return analyse.sentiment.polarity


# TextBlob wird angewiesen den Text in der entsprechenden Zeile auszulesen
# GerVader analysiert den Text in der entsprechenden Zeile
# Die normierte, numerische Bewertung wird von -1 bis
# Die Zeilen der in der Tabbelle auszugebenden Werte werden formatiert


def score_normiert_berechnen(zeile: Series):
    return skala_anpassen(
        float(zeile[str(Spalten.numerischer_wert)]),
        float(zeile[str(Spalten.skala_von)]),
        float(zeile[str(Spalten.skala_bis)]),
        -1,
        1
    )


def sentiment_scores_berechnen(bewertungen: DataFrame):
    sentiment_scores = DataFrame()
    sentiment_scores[str(Spalten.nutzer_score_normiert)] = bewertungen.apply(score_normiert_berechnen, axis=1)
    sentiment_scores[str(Spalten.zu_bewertender_text)] = (bewertungen[str(Spalten.text_titel)]
                                                          + '. ' + bewertungen[str(Spalten.text_allgemein)]
                                                          + '. ' + bewertungen[str(Spalten.text_positiv)]
                                                          + '. ' + bewertungen[str(Spalten.text_negativ)])
    sentiment_scores[str(Spalten.zu_bewertender_text)] = sentiment_scores[str(Spalten.zu_bewertender_text)].apply(
        lambda text: ' '.join(text_bereinigen(text))
    )
    monat_und_jahr_ergaenzen(sentiment_scores, bewertungen[str(Spalten.reise_monat)])

    for methode in AnalyseMethode:
        sentiment_scores[f"Score: {methode}"] = sentiment_scores.apply(score_berechnen_mit_methode, args=(methode,),
                                                                       axis=1)
        sentiment_scores[f"Diskrepanz: {methode}"] = abs(
            sentiment_scores[f"Score: {methode}"] - sentiment_scores[str(Spalten.nutzer_score_normiert)])

    return sentiment_scores


# Um eine Auswertung nach Monaten zu erstellen: Monat  und Jahr trennen
def monat_und_jahr_ergaenzen(sentiment_scores: DataFrame, reise_monate: Series):
    reise_monate = reise_monate.apply(
        lambda x: f"{list(monate.keys())[x.month - 1]} {x.year}" if isinstance(x, datetime.datetime) else x)

    sentiment_scores[["Monat", "Jahr"]] = reise_monate.str.split(" ", expand=True)

    sentiment_scores['Monat'] = sentiment_scores['Monat'].map(monate)


def plot_anzeigen_und_speichern(ordner_pfad: str, datei_name: str):
    figure = plt.gcf()
    plt.show()
    figure.savefig(f"{ordner_pfad}/{datei_name}")


def zeilen_ohne_text_entfernen(sentiment_scores: DataFrame):
    erforderliche_spalten = [
        str(Spalten.text_allgemein),
        str(Spalten.text_positiv),
        str(Spalten.text_negativ),
    ]
    return sentiment_scores[
        sentiment_scores[erforderliche_spalten].apply(lambda wert: any(wert != ""), axis=1)]


# VISUALISIERUNG
# Auswertung 1: Durchschnittlicher numerischer und Sentiment-Score und pro Monat (gegliedert in Jahren)
def plot_scores_pro_monat(sentiment_scores: DataFrame, ordner_pfad: str):
    sentiment_scores = zeilen_ohne_text_entfernen(sentiment_scores)
    sentiment_scores_nach_jahren = sentiment_scores.groupby('Jahr')

    anzahl_jahre = len(sentiment_scores_nach_jahren.indices)
    hoehe_pro_jahr = 4
    fig, subplots = plt.subplots(
        nrows=len(sentiment_scores_nach_jahren),
        ncols=1,
        figsize=(16, anzahl_jahre * hoehe_pro_jahr),
        sharex=True,
        sharey=True
    )

    plt.xlabel('Monat')
    plt.ylabel('Score')
    suptitle = plt.suptitle(f'Numerische und textuelle Bewertungen (Durchschnitt)')
    suptitle.set_y(1)

    vorhandene_monate = sentiment_scores['Monat'].replace('', -1).unique()
    plt.xticks(
        range(1, vorhandene_monate.size + 1) if vorhandene_monate.size == 12 else range(vorhandene_monate.size),
        list(map(
            lambda zahl: monats_name(zahl),
            numpy.sort(vorhandene_monate)
        )),
        rotation=90
    )
    plt.tight_layout()

    for i, (jahr, scores_pro_jahr) in enumerate(sentiment_scores_nach_jahren):
        scores_pro_monat = scores_pro_jahr.groupby('Monat')
        sentiment_scores_pro_monat = scores_pro_monat[f"Score: {bevorzugte_analyse_methode}"].mean()
        numerische_scores_pro_monat = scores_pro_monat[str(Spalten.nutzer_score_normiert)].mean()
        # numerische_scores_pro_monat_max = scores_pro_jahr.groupby('Monat')[str(Spalten.nutzer_score_normiert)].max()
        # numerische_scores_pro_monat_min = scores_pro_jahr.groupby('Monat')[str(Spalten.nutzer_score_normiert)].min()

        subplots[i].plot(
            sentiment_scores_pro_monat.index,
            sentiment_scores_pro_monat.values,
            marker='o',
            linestyle='-',
        )
        subplots[i].plot(
            numerische_scores_pro_monat.index,
            numerische_scores_pro_monat.values,
            marker='o',
            linestyle='-',
            color='orange'
        )

        anzahl_bewertungen_pro_monat = scores_pro_monat.size()

        for x, y, label in zip(sentiment_scores_pro_monat.index, sentiment_scores_pro_monat.values,
                               anzahl_bewertungen_pro_monat):
            subplots[i].annotate(label, (x, y), textcoords="offset points", xytext=(0, 10), ha='center')

        subplots[i].legend(title=jahr, loc='upper right')

        for x in sentiment_scores['Monat'].unique():
            subplots[i].axvline(x=x, color='gray', linestyle='--', alpha=0.5)

    farb_infos = [
        # C0 = Standardfarbe von matplotlib
        Line2D([0], [0], color="C0", lw=2),
        Line2D([0], [0], color="orange", lw=2),
        # Line2D([0], [0], color="C0", lw=2, alpha=0.1),
    ]
    fig.legend(
        farb_infos,
        ["Sentiment-Score", "Numerischer Wert (normiert)"],
        loc='upper right'
    )

    plot_anzeigen_und_speichern(ordner_pfad, 'plot_sentiment_scores_pro_monat.png')


def plot_szenario_8(sentiment_scores: DataFrame, ordner_pfad: str):
    for spalte in [str(Spalten.nutzer_score_normiert), f"Score: {bevorzugte_analyse_methode}"]:
        sentiment_scores = zeilen_ohne_text_entfernen(sentiment_scores)
        sentiment_scores_nach_jahren = sentiment_scores.groupby('Jahr')

        anzahl_jahre = len(sentiment_scores_nach_jahren.indices)
        hoehe_pro_jahr = 4
        fig, subplots = plt.subplots(
            nrows=len(sentiment_scores_nach_jahren),
            ncols=1,
            figsize=(16, anzahl_jahre * hoehe_pro_jahr),
            sharex=True,
            sharey=True
        )

        plt.xlabel('Monat')
        plt.ylabel('Score')
        suptitle = plt.suptitle(f'{spalte} (Durchschnitt)')
        suptitle.set_y(1)

        vorhandene_monate = sentiment_scores['Monat'].replace('', -1).unique()
        plt.xticks(
            range(1, vorhandene_monate.size + 1) if vorhandene_monate.size == 12 else range(vorhandene_monate.size),
            list(map(
                lambda zahl: monats_name(zahl),
                numpy.sort(vorhandene_monate)
            )),
            rotation=90
        )
        plt.tight_layout()

        for i, (jahr, scores_pro_jahr) in enumerate(sentiment_scores_nach_jahren):
            sentiment_scores_nach_portal = scores_pro_jahr.sort_values(['Portal']).groupby(str(Spalten.portal))
            for p, (portal, scores_pro_portal) in enumerate(sentiment_scores_nach_portal):
                scores_pro_monat = scores_pro_portal.sort_values(['Monat']).groupby('Monat')

                scores = scores_pro_monat[spalte].mean()

                subplots[i].plot(
                    scores.index,
                    scores.values,
                    marker='o',
                    linestyle='-',
                )

                anzahl_bewertungen_pro_monat = scores_pro_monat.size()

                for x, y, label in zip(scores.index, scores.values,
                                       anzahl_bewertungen_pro_monat):
                    subplots[i].annotate(label, (x, y), textcoords="offset points", xytext=(0, 10), ha='center')

                subplots[i].legend(title=jahr, loc='upper right')

                for x in sentiment_scores['Monat'].unique():
                    subplots[i].axvline(x=x, color='gray', linestyle='--', alpha=0.5)

        farb_infos = [
            # C0 = Standardfarbe von matplotlib
            Line2D([0], [0], color="C0", lw=2),
            Line2D([0], [0], color="orange", lw=2),
        ]
        fig.legend(
            farb_infos,
            numpy.unique(sentiment_scores[str(Spalten.portal)].values.tolist()),
            loc='upper right'
        )

        plot_anzeigen_und_speichern(ordner_pfad, f"szenario_8_{spalte}.png")


def spalte_sortieren(sentiment_scores: DataFrame, spalte: str):
    if spalte == str(Spalten.reise_dauer) or spalte == str(Spalten.autor_altersgruppe):
        def numerisch_sortieren(text):
            match = re.match(r'^(\d+)', text)
            if match:
                return int(match.group(1))
            else:
                return None

        sentiment_scores[str(Spalten.sortierung)] = sentiment_scores[spalte].apply(numerisch_sortieren)
        sentiment_scores = sentiment_scores.sort_values(by=str(Spalten.sortierung))
        sentiment_scores = sentiment_scores.drop(columns=str(Spalten.sortierung))
    else:
        def nach_anzahl_sortieren(text):
            return sentiment_scores[sentiment_scores[spalte] == text].size

        sentiment_scores[str(Spalten.sortierung)] = sentiment_scores[spalte].apply(nach_anzahl_sortieren)
        sentiment_scores = sentiment_scores.sort_values(by=str(Spalten.sortierung), ascending=False)
        sentiment_scores = sentiment_scores.drop(columns=str(Spalten.sortierung))

    return sentiment_scores


# Auswertung 2: Durchschnittlicher Sentiment-Score pro Monat (gegliedert in Jahren)
def plot_durchschnittliche_sentiment_scores_nach_spalte(sentiment_scores: DataFrame, spalte: str,
                                                        ordner_pfad: str):
    # Nach spalte und Portal gruppieren, Durchschnitt und Anzahl berechnen
    nach_spalte_und_portal = sentiment_scores.groupby([spalte, "Portal"])["Score: gervader"].agg(
        ['mean', 'count']).unstack()

    anzahl_spalten_werte = len(nach_spalte_und_portal.index)
    fig, ax = plt.subplots(figsize=(8 if anzahl_spalten_werte < 15 else 16, 8),
                           constrained_layout=True)

    # Für jedes Portal und jeden Wert einen Balken erstellen
    portale = nach_spalte_und_portal.columns.levels[1]

    def balken_indizes_berechnen(werte: Series):
        return Series({spalte: i + 1 for i, spalte in enumerate(werte.index) if not numpy.isnan(werte[spalte])})

    balken_indizes = nach_spalte_und_portal['mean'].apply(balken_indizes_berechnen, axis=1).fillna(0)
    balken_pro_wert = list(map(numpy.max, balken_indizes.values))
    for i, portal in enumerate(portale):
        balken_breite = 0.2
        balken_x = [
            wert_index + (balken_index - 0.5) * balken_breite - (anzahl_balken / 2 * balken_breite) for
            wert_index, balken_index, anzahl_balken in
            zip(range(anzahl_spalten_werte), balken_indizes[portal].values, balken_pro_wert)
        ]
        balken = ax.bar(balken_x, nach_spalte_und_portal[('mean', portal)], width=balken_breite, label=portal)

        # Anzahl zu Balken hinzufügen
        for balken_aktuell, pos, anzahl in zip(balken, balken_x, nach_spalte_und_portal[('count', portal)]):
            if (numpy.isnan(anzahl) == False):
                breite = balken_aktuell.get_width()
                hoehe = balken_aktuell.get_height()
                x = balken_aktuell.get_x()
                y = hoehe if hoehe > 0 else hoehe * 1.07
                ax.annotate(f'{int(anzahl)}', xy=(x + breite / 2, y),
                            xytext=(0, 3), textcoords='offset points',
                            size='x-small', ha='center', va='bottom')

    x_achse_name = spalten_name_fuer_plot(spalte)
    ax.set_title(f'Nach {x_achse_name}')
    ax.set_xlabel(x_achse_name)
    ax.set_ylabel('Durchschn. Sentiment-Score')
    x_ticks_positionen = range(anzahl_spalten_werte)
    ax.set_xticks(x_ticks_positionen)
    ax.set_xticklabels(nach_spalte_und_portal.index)
    ax.legend(loc='upper right')
    plt.xticks(rotation=90)

    plot_anzeigen_und_speichern(ordner_pfad, f"plot_{spalte}.png")


# Auswertung 2: Durchschnittlicher Sentiment-Score pro Monat (gegliedert in Jahren)
def scatter_plot_spalte(sentiment_scores: DataFrame, spalte: str,
                        ordner_pfad: str):
    sentiment_scores = spalte_sortieren(sentiment_scores, spalte)
    sortier_spalten_werte = sentiment_scores[spalte].unique().tolist()
    sortier_spalten_werte_mit_anzahl = list(map(
        lambda x: f"{x} ({sentiment_scores[sentiment_scores[spalte] == x][spalte].size})",
        sortier_spalten_werte
    ))
    unique, counts = numpy.unique(sentiment_scores[spalte], return_counts=True)

    # Set up logarithmic scaling for the size of data points
    sizes = numpy.log(counts) * 40  # Adjust the factor to scale the sizes properly
    cmap = plt.get_cmap('viridis')

    plt.subplots(figsize=(8 if len(sortier_spalten_werte_mit_anzahl) < 15 else 16, 8), constrained_layout=True)
    plt.xlabel(spalten_name_fuer_plot(spalte))
    plt.ylabel('Sentiment-Score')
    plt.suptitle(f'Nach {spalten_name_fuer_plot(spalte)}')
    # plt.tight_layout(fig)
    plt.xticks(range(len(sortier_spalten_werte_mit_anzahl)), sortier_spalten_werte_mit_anzahl, rotation=90)
    plt.scatter(
        x=sentiment_scores[spalte],
        y=sentiment_scores[f"Score: {bevorzugte_analyse_methode}"],
        # sizes=sizes,
        # c=counts,
        cmap=cmap
    )
    plot_anzeigen_und_speichern(ordner_pfad, f"scatter_{spalte}.png")


# Auswertung 2: Häufigste Wörter (jeweils positiv und negativ)
def plot_top_sentiment_woerter(sentiment_scores: DataFrame, ordner_pfad: str):
    sentiment_scores = zeilen_ohne_text_entfernen(sentiment_scores)

    # Positivste Wörter
    woerter_in_text_positiv = sentiment_scores[str(Spalten.text_positiv)].apply(text_bereinigen).explode().tolist()
    woerter_in_text_negativ = sentiment_scores[str(Spalten.text_negativ)].apply(text_bereinigen).explode().tolist()
    woerter_in_positiven_bewertungen = sentiment_scores[sentiment_scores[f"Score: {AnalyseMethode.gervader}"] > 0][
        str(Spalten.zu_bewertender_text)].apply(text_bereinigen).explode().tolist()
    woerter_in_negativen_bewertungen = sentiment_scores[sentiment_scores[f"Score: {AnalyseMethode.gervader}"] < 0][
        str(Spalten.zu_bewertender_text)].apply(text_bereinigen).explode().tolist()

    def haeufigste_woerter_finden(woerter: list[str]):
        counter = Counter(woerter)
        haeufigste_woerter = counter.most_common(10)
        return haeufigste_woerter

    haeufigste_woerter_data_frame = DataFrame()
    haeufigste_woerter_data_frame["Häufigste Wörter in Spalte 'Text positiv"] = haeufigste_woerter_finden(
        woerter_in_text_positiv)
    haeufigste_woerter_data_frame["Häufigste Wörter in Spalte 'Text negativ"] = haeufigste_woerter_finden(
        woerter_in_text_negativ)
    haeufigste_woerter_data_frame["Häufigste Wörter in positiven Bewertungen"] = haeufigste_woerter_finden(
        woerter_in_positiven_bewertungen)
    haeufigste_woerter_data_frame["Häufigste Wörter in negativen Bewertungen"] = haeufigste_woerter_finden(
        woerter_in_negativen_bewertungen)

    data_frame_speichern(haeufigste_woerter_data_frame, '/'.join([ordner_pfad, "haeufigste_woerter.xlsx"]))


def spalte_leer(spalte: Series):
    return set(spalte) == {''}


def nach_spalte_filtern(data_frame: DataFrame, spalte: str) -> DataFrame:
    return data_frame[data_frame[spalte] != ""]


def f1_score_berechnen(sentiment_scores: DataFrame):
    true_positives = sentiment_scores[
        (sentiment_scores[str(Spalten.nutzer_score_normiert)] > 0) &
        (sentiment_scores[f"Score: {bevorzugte_analyse_methode}"] > 0)
        ]
    true_negatives = sentiment_scores[
        (sentiment_scores[str(Spalten.nutzer_score_normiert)] < 0) &
        (sentiment_scores[f"Score: {bevorzugte_analyse_methode}"] < 0)
        ]
    false_positives = sentiment_scores[
        (sentiment_scores[str(Spalten.nutzer_score_normiert)] < 0) &
        (sentiment_scores[f"Score: {bevorzugte_analyse_methode}"] > 0)
        ]
    false_negatives = sentiment_scores[
        (sentiment_scores[str(Spalten.nutzer_score_normiert)] > 0) &
        (sentiment_scores[f"Score: {bevorzugte_analyse_methode}"] < 0)
        ]

    precision = true_positives.size / (true_positives.size + false_positives.size)
    recall = true_positives.size / (true_positives.size + false_negatives.size)
    accuracy = (true_positives.size + true_negatives.size) / (
            true_positives.size + false_negatives.size + true_negatives.size + false_positives.size)
    f1_score = (2 * precision * recall) / (precision + recall)

    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'accuracy': accuracy
    }


# Auswertung 3: Untersuchung weiterer Parameter: Z.B. Nach Monaten analysieren oder nach Altersgruppen
def analyse(sentiment_scores: DataFrame, ordner_pfad: str):
    plot_scores_pro_monat(sentiment_scores.copy(), ordner_pfad)
    plot_szenario_8(sentiment_scores.copy(), ordner_pfad)

    auszuwertende_spalten = [
        str(Spalten.reise_gruppe),
        str(Spalten.reise_dauer),
        str(Spalten.reise_absicht),
        str(Spalten.autor_nationalitaet),
        str(Spalten.autor_altersgruppe)
    ]

    for spalte in auszuwertende_spalten:
        if spalte in sentiment_scores.columns:
            nicht_leere_zeilen = nach_spalte_filtern(sentiment_scores.copy(), spalte)

            if nicht_leere_zeilen.size:
                plot_durchschnittliche_sentiment_scores_nach_spalte(nicht_leere_zeilen, spalte, ordner_pfad)
                scatter_plot_spalte(nicht_leere_zeilen, spalte, ordner_pfad)

    plot_top_sentiment_woerter(sentiment_scores.copy(), ordner_pfad)


def reise_dauer_normieren(sentiment_scores: DataFrame):
    wochen_format = re.compile(r'(\d)\sWochen?')

    def wochen_in_naechte_umwandeln(reise_dauer: str):
        match = wochen_format.match(reise_dauer)
        wochen = int(match.group(1))
        naechte = (wochen * 7) - 1
        return f"{naechte} Nächte"

    sentiment_scores[str(Spalten.reise_dauer)] = sentiment_scores[str(Spalten.reise_dauer)].apply(
        lambda reise_dauer: wochen_in_naechte_umwandeln(reise_dauer) if wochen_format.match(
            reise_dauer) is not None else reise_dauer
    )


def portal_ergaenzen(sentiment_scores: DataFrame):
    sentiment_scores[str(Spalten.portal)] = sentiment_scores.apply(
        lambda zeile: 'HolidayCheck' if zeile[str(Spalten.skala_bis)] == 6.0 else 'Booking.com',
        axis=1
    )


def main():
    scraper_ergebnis_datei_pfad = datei_pfad_laden()
    ordner_pfad = '/'.join(scraper_ergebnis_datei_pfad.split('/')[:-1])
    sentiment_scores_datei_pfad = '/'.join([ordner_pfad, "sentiment-scores.xlsx"])
    bewertungen = data_frame_laden(scraper_ergebnis_datei_pfad)

    if os.path.exists(sentiment_scores_datei_pfad):
        sentiment_scores = data_frame_laden(sentiment_scores_datei_pfad)
    else:
        sentiment_scores = sentiment_scores_berechnen(bewertungen)

        # Die formatierten Daten in einer Excel-Tabelle ausgeben
        print(f"Bewertungen mit sentiment scores nach \"{sentiment_scores_datei_pfad}\" speichern")
        data_frame_speichern(sentiment_scores, sentiment_scores_datei_pfad)

    bewertungen_mit_sentiment_scores = sentiment_scores.join(bewertungen)
    methoden_vergleichen(bewertungen_mit_sentiment_scores)
    portal_ergaenzen(bewertungen_mit_sentiment_scores)
    reise_dauer_normieren(bewertungen_mit_sentiment_scores)
    analyse(bewertungen_mit_sentiment_scores, ordner_pfad)


main()
