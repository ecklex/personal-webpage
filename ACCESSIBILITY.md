# Barrierefreiheit

Diese Seite verkauft BFSG-/WCAG-Kompetenz — deshalb wird sie selbst nach
**WCAG 2.1 AA** gepflegt und regelmäßig auf der *live ausgelieferten* Fassung
auditiert (nicht nur in den Quelldateien). Diese Datei dokumentiert, was geprüft
wurde und mit welchem Ergebnis. Letztes Audit: Juli 2026.

## Geprüft und konform

| Kriterium (WCAG 2.1) | Umsetzung | Status |
|---|---|---|
| **1.1.1** Nicht-Text-Inhalte | Profilbild mit `alt`-Text; Demo-Videos mit `aria-label` **und** Textbeschreibung (`<figcaption>`) | ✅ |
| **1.2.1** Video (nur Bild) | Videos haben **keinen Ton**; die Textbeschreibung unter jedem Video ist die gleichwertige Alternative — kein `<track>` nötig | ✅ |
| **1.3.1** Info & Beziehungen | Genau **ein** `<h1>` (Theme-Banner-H1 im Layout entfernt); Hierarchie `h1 → h2 → h3` ohne Sprünge; Formularfelder mit verknüpftem `<label>`; `<main>`-Landmark; Footer-`<nav aria-label>` | ✅ |
| **1.4.3** Kontrast (Minimum) | siehe Kontrasttabelle unten — alle Werte ≥ Schwelle | ✅ |
| **2.4.1** Blöcke umgehen | „Zum Inhalt springen"-Skip-Link, wird bei Fokus sichtbar | ✅ |
| **2.4.4** Linkzweck | Aussagekräftige Linktexte, keine nackten URLs, `rel="noopener"` | ✅ |
| **2.4.7** Fokus sichtbar | `:focus-visible`-Outline 3px `#0b5c5c` (7,78:1) auf Links, Buttons, Feldern, Video | ✅ |
| **3.1.1** Sprache der Seite | `<html lang="de">` | ✅ |
| **3.3.2** Beschriftungen | Alle Eingabefelder mit sichtbarem `<label>`; Platzhalter nur ergänzend | ✅ |
| **4.1.3** Statusmeldungen | Formular-Status über `role="status"` / `aria-live="polite"` | ✅ |

## Kontrastwerte (gegen Weiß, gemessen)

| Element | Farbe | Ratio | Schwelle | |
|---|---|---|---|---|
| Fließtext | `#606c71` | 5,41:1 | 4,5 | ✅ |
| Überschriften h1–h3 | `#0b6b3a` | 6,61:1 | 4,5 | ✅ |
| Body-Links | `#1e6bb8` | 5,45:1 | 4,5 | ✅ |
| Karten-Links | `#0066cc` | 5,57:1 | 4,5 | ✅ |
| Sekundärtext (Org, Stack, Quelle) | `#586069` | 6,38:1 | 4,5 | ✅ |
| Datumsangaben | `#6a737d` | 4,82:1 | 4,5 | ✅ |
| Status „Offen für …" | `#1a7f37` | 5,08:1 | 4,5 | ✅ |
| Skip-Link fokussiert | `#24292e` auf `#e19447` | 8,53:1 | 4,5 | ✅ |

## Behobene Befunde (Audit Juli 2026)

- **Skip-Link fokussiert war 2,21:1** (Cayman-Standard: blauer Text auf orangem
  Grund) → Textfarbe auf dunkel gesetzt (8,53:1). *War der einzige echte
  AA-Verstoß.*
- **Überschriften-Grün `#159957` = 3,67:1** bestand nur als Großtext → auf
  `#0b6b3a` (6,61:1) abgedunkelt, damit auch die neuen `<h3>` sicher bestehen.
- **Tagline** war als `<h2>` ausgezeichnet → auf `<p class="subtitle">` geändert,
  damit die Überschriften-Navigation nur echte Abschnitte listet.
- **Projekt-/Positionstitel** waren `<strong>` → jetzt `<h3>`, sodass Screenreader
  zwischen Projekten und Stationen springen können.

## Bekannte, bewusste Entscheidungen

- **Video-Untertitel (`<track>`):** Nicht vorhanden, weil die Videos keinen Ton
  haben; die Textbeschreibung ist die konforme Alternative (SC 1.2.1). Automatische
  Tools (axe/Lighthouse) können das dennoch als Hinweis anzeigen — das ist ein
  False Positive.
- **Englische Fachbegriffe** („AI Enablement", „Content Operations", „Prompt
  Engineering") ohne `lang="en"` (SC 3.1.2): überwiegend Eigen-/Produktnamen bzw.
  etablierte Lehnwörter. Bewusst nicht ausgezeichnet.
- **Video-Poster:** Aktuell `preload="metadata"` (erstes Frame als Vorschau); ein
  dediziertes Poster kann über das `video_poster`-Feld pro Karte ergänzt werden.

## Prüfung wiederholen

Nach Änderungen an Layout oder Farben:

1. Seite lokal bauen (`bundle exec jekyll serve`).
2. Lighthouse-Accessibility-Audit oder axe DevTools auf der gerenderten Seite.
3. Einmal komplett per Tastatur durchtabben (Skip-Link → Inhalt → Formular → Footer).
