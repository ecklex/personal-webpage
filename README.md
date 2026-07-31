# personal-webpage

Personal website and CV for Alexander Eckerlin, built with [Jekyll](https://jekyllrb.com/) and hosted on [GitHub Pages](https://pages.github.com/).

🔗 **Live site:** [ecklex.github.io/personal-webpage](https://ecklex.github.io/personal-webpage)

## Tech Stack

- **Generator:** Jekyll (via GitHub Pages)
- **Theme:** [Cayman](https://github.com/pages-themes/cayman) (`pages-themes/cayman@v0.2.0`)
- **Hosting:** GitHub Pages

## Local Development

1. Install [Ruby](https://www.ruby-lang.org/) and [Bundler](https://bundler.io/).
2. Create a `Gemfile` (if not already present):
   ```ruby
   source "https://rubygems.org"
   gem "github-pages", group: :jekyll_plugins
   ```
3. Install dependencies:
   ```bash
   bundle install
   ```
4. Serve locally:
   ```bash
   bundle exec jekyll serve
   ```
5. Open `http://localhost:4000` in your browser.

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

## Deployment

Any push to the `main` branch is automatically deployed to GitHub Pages.
