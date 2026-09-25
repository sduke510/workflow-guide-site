# Affiliate Product Pipeline

Stand: 26.09.2026

## Ziel

Der Pinterest-Workflow soll nicht einfach viele Pins erzeugen, sondern nur Inhalte veröffentlichen, die einen konkreten Kaufanreiz haben und sauber nachvollziehbar sind.

Aktueller PRE_API-Modus:

1. Produkt wird manuell in `Manual_Intake` erfasst.
2. Produktdaten landen in `Product_DB`.
3. Für geeignete Produkte werden Content-Kandidaten erstellt.
4. QA prüft Pflichtfelder, Kennzeichnung, Zielseite und Bild.
5. Jeder neue Pin benötigt vor der Veröffentlichung eine konkrete Freigabe.
6. Visual wird erzeugt oder als lizenzierte Editorial-Grafik hinterlegt.
7. Make veröffentlicht nur Datensätze mit `READY_TO_PUBLISH`.
8. Pin-ID und Zeit werden in `Automation_Queue` zurückgeschrieben.
9. Klicks/Conversions werden später über Pinterest/Amazon ausgewertet.

## Harte Publishing-Gates

Ein Pin darf NICHT veröffentlicht werden, wenn eines davon fehlt:

- öffentlich erreichbare `Image_URL`
- klarer Titel
- klare Beschreibung
- sichtbare Werbekennzeichnung
- funktionierende Zielseite
- eindeutige UTM-/Content-ID
- erlaubte Bildnutzung
- Board-ID

Das Bild muss eine echte visuelle Funktion erfüllen. Leere Pins, reine Platzhalter und generische Testgrafiken sind keine veröffentlichungsfähigen Creatives.

## Bildstrategie

Solange Amazon Creators/PA-API noch nicht verfügbar ist:

- keine kopierten Amazon-Produktbilder herunterladen oder auf Pinterest neu hosten
- stattdessen eigene oder lizenzierte Editorial-Bilder nutzen
- generische Bilder immer als Stimmungsbild behandeln, nie als exakte Produktabbildung
- bei erkennbaren Personen, Logos oder Marken zusätzliche Rechte prüfen
- für Produktseiten kann ein Editorial-Bild verwendet werden, wenn die Kennzeichnung eindeutig ist

Sobald eine zulässige Amazon-Schnittstelle Produktbilder bereitstellt, kann das Bildsystem neu bewertet werden.

## Landingpage-Prinzip

Die Zielseite soll kein langer Umweg sein. Der erste sichtbare Bereich enthält:

- großes relevantes Bild
- klaren Produktbezug
- kurze Nutzenbeschreibung
- sichtbaren Affiliate-Hinweis
- großen Amazon-CTA

Der Amazon-Button steht oberhalb der Falz. Auf Mobilgeräten gibt es zusätzlich eine Sticky-CTA-Leiste.

## Farben

- Bordeaux: `#6f2337`
- dunkles Bordeaux: `#4b1725`
- Olive: `#7b813f`
- dunkles Olive: `#555b28`
- Creme: `#faf7f0`

Die Farben sind in `assets/style.css` zentral definiert.

## Relevante Dateien

- `assets/style.css` – globales Theme + Produkt-Landingpage-Komponenten
- `templates/product-landing.html` – wiederverwendbare Vorlage
- `pages/oktoberfest-dirndl-bluse.html` – erster produktorientierter Test
- `affiliate-hinweis.html` – Transparenzseite

## Google-Sheet-Status

Wichtige Statuswerte:

- `DRAFT` – noch nicht QA-fertig
- `AWAITING_APPROVAL` – inhaltlich vorbereitet, wartet auf menschliche Freigabe
- `READY_FOR_DESIGN` – Freigabe vorhanden, Visual fehlt noch
- `READY_TO_PUBLISH` – alle Gates erfüllt
- `PUBLISHED` – von Pinterest bestätigt

Ein Datensatz mit leerer `Image_URL` darf niemals auf `READY_TO_PUBLISH` gesetzt werden.

## Aktueller Proof of Concept

Produkt:
- Product_ID: `P001`
- ASIN: `B0HD7BVTKZ`
- Zielseite: `pages/oktoberfest-dirndl-bluse.html`

Der alte Pin `Q130` wurde mit einer Platzhaltergrafik veröffentlicht und dient nicht als Qualitätsstandard.

Der vorbereitete Ersatzpin `Q145` nutzt ein lizenziertes Editorial-Foto einer weißen Bluse und steht auf `AWAITING_APPROVAL`.

## Nächste technische Stufe

Sobald Amazon den API-Zugang freischaltet:

- manuelle Produkterfassung durch Creators/PA-API-Suche ersetzen
- ASIN-Deduplizierung beibehalten
- Produktdaten automatisch aktualisieren
- Bilder nur über ausdrücklich zulässige Quellen verwenden
- Landingpage und Pinterest-Workflow unverändert weiterverwenden
