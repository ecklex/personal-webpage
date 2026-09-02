# personal-webpage

Personal website and CV for Alexander Eckerlin, built with [Jekyll](https://jekyllrb.com/) and hosted on [GitHub Pages](https://pages.github.com/).

🔗 **Live site:** [ecklex.github.io/personal-webpage](https://ecklex.github.io/personal-webpage)

## Tech Stack

- **Generator:** Jekyll (via GitHub Pages)
- **Theme:** [Cayman](https://github.com/pages-themes/cayman) (`pages-themes/cayman@v0.2.0`)
- **Hosting:** GitHub Pages

## Local Development

1. Install [Ruby](https://www.ruby-lang.org/) and [Bundler](https://bundler.io/).
   **Ruby 3.x, nicht 4.x:** das `github-pages`-Gem haengt ueber `jekyll-commonmark`
   an `commonmarker`, das `Ruby < 4.0` verlangt — mit Ruby 4 scheitert schon die
   Aufloesung der Abhaengigkeiten. Das System-Ruby von macOS (2.6) ist umgekehrt zu
   alt. Getestet mit 3.4 (`brew install ruby@3.4`, dann `/usr/local/opt/ruby@3.4/bin`
   in den PATH).
2. Install dependencies:
   ```bash
   bundle install
   ```
3. Serve locally:
   ```bash
   bundle exec jekyll serve
   ```
4. Open `http://localhost:4000` in your browser.

## Inhalte pflegen (Single Source of Truth)

Alle Inhalte liegen in **`_data/content.yml`**. Aus dieser einen Datei entstehen:

1. die **Website** (`index.html` rendert die Sektionen),
2. **`llms.txt`** (Klartextfassung für LLMs/KI-Recruiting),
3. das **CV-PDF** (`scripts/generate_cv.py` → HTML → WeasyPrint → PDF/UA-1).

Inhalt also **nur an einer Stelle** ändern: in `content.yml`. Website, llms.txt und
PDF ziehen automatisch nach.

## CV-PDF aktualisieren

Das PDF unter `assets/cv-alexander-eckerlin.pdf` wird **nicht von Hand** gepflegt,
sondern automatisch als **getaggtes, barrierefreies PDF/UA-1** erzeugt:

- `scripts/generate_cv.py` baut aus `content.yml` semantisches HTML und rendert es
  mit **WeasyPrint** zu einem PDF mit Strukturbaum, Überschriften-Tags, Lese­reihenfolge,
  Dokumentsprache (`/Lang`) und Alt-Text fürs Foto. (Früher lief das über LaTeX/XeLaTeX —
  das erzeugt aber nur *untagged*, nicht barrierefreie PDFs.)
- Die GitHub Action **`.github/workflows/generate-pdf.yml`** läuft bei jedem Push auf
  `main` (und manuell über „Run workflow"): PDF erzeugen → mit
  `scripts/verify_pdf_a11y.py` prüfen, dass es getaggt ist → nach `assets/` kopieren →
  zurückcommitten (`chore: auto-generate CV PDF [skip ci]`). Ist das PDF nicht getaggt,
  **bricht der Build ab**.
- **Konsequenz:** Nach einer Inhaltsänderung genügt der Push — das PDF aktualisiert
  sich selbst. Das eingecheckte PDF kann kurzzeitig hinter `content.yml` liegen, bis
  die Action durch ist.
- **Lokal testen:** `pip install -r scripts/requirements.txt && python scripts/generate_cv.py`
  erzeugt `cv.pdf` (gitignored). WeasyPrint braucht die Pango-Bibliotheken
  (macOS: `brew install pango`, Ubuntu: `libpango-1.0-0 libpangocairo-1.0-0`).

## Bewerbung zusammenstellen

Für eine konkrete Bewerbung ist der vollständige CV meist zu viel. Der **Bewerbungs-Builder**
erzeugt stattdessen ein PDF aus einem individuellen Anschreiben plus genau den Einträgen, die
zur Stelle passen — ebenfalls als getaggtes PDF/UA-1.

Er ist ein **rein lokales Werkzeug und nicht Teil der Website** — er hat mit Jekyll nichts zu
tun, sondern bringt einen eigenen kleinen Server mit (nur auf `127.0.0.1` erreichbar). Der
Ordner `bewerbungen/` steht in `.gitignore` und in `exclude:` von `_config.yml`: Anschreiben,
Firmennamen und die Absenderanschrift verlassen dieses (öffentliche) Repo nie.

**Einmalig:** Absenderanschrift anlegen —
`cp scripts/absender.example.yml bewerbungen/absender.yml` und ausfüllen.
Name und E-Mail zieht das Skript aus `content.yml`.

**Pro Bewerbung — ein Befehl:**

```bash
python scripts/bewerbung.py
```

Der Browser geht auf. Anschreiben schreiben, Einträge an- und abwählen, Sektionsreihenfolge
festlegen, „PDF erzeugen“ klicken. Das PDF landet in `bewerbungen/` und öffnet sich; Strg+C
beendet den Server.

Die Auswahl wird dabei zusätzlich als YAML in `bewerbungen/` abgelegt. Am Anschreiben lässt
sich dort im Editor weiterschreiben — neu bauen dann ohne Browser:

```bash
python scripts/generate_application.py bewerbungen/<datei>.yml
```

Prüfen wie beim CV: `python scripts/verify_pdf_a11y.py bewerbungen/<datei>.pdf`.

Auswahl und Reihenfolge hängen an den `id`-Feldern in `content.yml`. Neue Einträge dort
brauchen also eine `id`; einmal vergebene sollten stabil bleiben, sonst laufen ältere
Bewerbungsdateien ins Leere (das Skript bricht dann mit einer Meldung ab, statt Einträge
stillschweigend wegzulassen).

## Deployment

Any push to the `main` branch is automatically deployed to GitHub Pages.
