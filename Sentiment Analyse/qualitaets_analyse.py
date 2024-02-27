import pandas as pd
from pandas import DataFrame, Series
from gemeinsame_funktionen import data_frame_laden, bevorzugte_analyse_methode, Spalten, datei_pfad_laden, \
    AnalyseMethode


def messkriterien_berechnen(sentiment_scores: DataFrame):
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

    auswertung = Series()
    auswertung['Precision'] = precision
    auswertung['Recall'] = recall
    auswertung['F1 Score'] = f1_score
    auswertung['Accuracy'] = accuracy

    print('\nMesskriterien')
    print(auswertung)


def methoden_vergleichen(sentiment_scores: DataFrame):
    auswertung = pd.DataFrame(index=['Median', 'Mittelwert'])
    for methode in AnalyseMethode:
        auswertung[methode] = [sentiment_scores[f"Diskrepanz: {methode}"].median(),
                               sentiment_scores[f"Diskrepanz: {methode}"].mean()]

    print('\nMethodenvergleich')
    print(auswertung)


def main():
    scraper_ergebnis_datei_pfad = datei_pfad_laden()
    ordner_pfad = '/'.join(scraper_ergebnis_datei_pfad.split('/')[:-1])
    sentiment_scores_datei_pfad = '/'.join([ordner_pfad, "sentiment-scores.xlsx"])
    bewertungen = data_frame_laden(scraper_ergebnis_datei_pfad)
    sentiment_scores = data_frame_laden(sentiment_scores_datei_pfad)
    bewertungen_mit_sentiment_scores = sentiment_scores.join(bewertungen)

    methoden_vergleichen(bewertungen_mit_sentiment_scores)
    messkriterien_berechnen(bewertungen_mit_sentiment_scores)


main()
