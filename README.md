# Anleitung zum Ausführen der Programme

## 1. Scraper
Die Scraper für booking.com und HolidayCheck sind in TypeScript geschrieben und öffnen beim Ausführen einen Browser, der automatisch Bewertungen ausliest und speichert.
Da bereits gescrapte Ergebnisse in diesem Repository vorhanden sind, kann dieser Schritt übersprungen werden.

### Schritte
1. Installieren Sie node.js in der Version 20 und pnpm in der Version 8.9.0.
    node.js ist eine Umgebung unter der JavaScript (und TypeScript) ausgeführt wird – npm hilft, Abhängigkeiten zu verwalten.
    Die Anleitungen finden sie unter [diesem Link für node.js](https://nodejs.org/en/learn/getting-started/how-to-install-nodejs) und [diesem Link für pnpm](https://pnpm.io/installation)
2. Öffnen Sie ein Termin im Ordner `Scraper` und führen sie den Befehl `pnpm install` aus. Dieser installiert alle Abhängigkeiten.
3. Die ausführbaren Scripte finden sich in der Datei `package.json`
    Führen Sie die Befehle mittels `pnpm run <Script Name>` im Terminal aus. Das Suffix `:ui` öffnet den Browser aus, sodass man den Scraping-Prozess beobachten kann. Die anderen Skripte führen das Scraping im Hintergrund aus.
4. Nach erfolgreichem Scrapen werden die resultierenden Excel-Dateien im Ordner `excel-dateien/<Hotel Name>/<Buchungsportal>/<Zeitstempel>/scraper-ergebnis.xlsx` gespeichert.

## 2. Sentimentanalyse
Die Sentimentanalyse wurde mit Python entwickelt. Python 3.9 muss also auf dem System vorhanden sein, um diese auszuführen.
Falls Python nicht vorinstalliert ist, bitte installieren Sie es mithilfe [der Dokumentation](https://wiki.python.org/moin/BeginnersGuide/Download).

### Schritte
1. Wechseln Sie im Terminal in den Ordner `Sentiment Analyse`.
2. Führen Sie das Python-Skript `hotel_sentiment_analyse.py` aus und geben Sie den Pfad zu der zu analysierenden Excel-Datei an.
    Beispiel:
    ```
    /usr/bin/python3 "/Users/zoescheer/Desktop/UNI Wien/Masterarbeit/Programm/Sentiment Analyse/hotel-sentiment-analyse.py" "../excel-dateien/Gasthof Goldene Traube/holiday-check/2024-02-07T19:03:44.596Z/scraper-ergebnis.xlsx"
    ```
3. Das Skript zeigt die einzelnen Arbeitsschritte in der Konsole an, so kann der Fortschritt verfolgt werden. Bei größeren Excel-Sheets kann der Prozess etwas länger dauern.
4. Nach erfolgreicher Analyse werden die Auswertungen als Excel-Datei, sowie Bilder für die Diagramme gespeichert. Die Ausgabe erfolgt im selben Ordner, in dem auch das Scraper-Ergebnis vorliegt.
