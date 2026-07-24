# Barrierefreiheit

Diese Seite verkauft BFSG-/WCAG-Kompetenz — deshalb wird sie selbst nach WCAG 2.1 AA
gepflegt. Diese Datei dokumentiert, was geprüft wurde und mit welchem Ergebnis.

| Kriterium (WCAG 2.1) | Umsetzung | Status |
|---|---|---|
| **1.1.1** Nicht-Text-Inhalte | Profilbild mit `alt`-Text; Demo-Videos mit `aria-label` **und** Textbeschreibung (`<figcaption>`) im Fließtext | ✅ |
| **1.3.1** Info und Beziehungen | Genau **ein** `<h1>` (Theme-Banner-H1 im Layout entfernt, nicht nur per CSS versteckt); Überschriftenhierarchie ohne Sprünge; Formularfelder mit verknüpften `<label>` | ✅ |
| **1.4.3** Kontrast (Minimum) | Fließtext, Links und Sekundärtext gegen Weiß auf ≥ 4.5:1 geprüft; Akzentfarbe auf `#0b5c5c` gesetzt | ✅ |
| **2.1.1** Tastatur | Alle interaktiven Elemente (Links, Formular, Video-Controls) per Tastatur erreichbar; kein Tastaturfallen | ✅ |
| **2.4.1** Blöcke umgehen | „Zum Inhalt springen"-Skip-Link (deutschsprachig) als erstes fokussierbares Element | ✅ |
| **2.4.4** Linkzweck | Aussagekräftige Linktexte (z. B. „AIdit auf GitHub", „Quellcode auf GitHub ansehen") — keine nackten URLs, kein „hier klicken" | ✅ |
| **2.4.7** Fokus sichtbar | Deutlicher `:focus-visible`-Outline auf Links, Buttons, Formularfeldern und Video | ✅ |
| **3.1.1** Sprache der Seite | `lang="de"` im `<html>` gesetzt | ✅ |
| **4.1.2** Name, Rolle, Wert | Formular-Status über `role="status"` / `aria-live="polite"` angekündigt | ✅ |

## Offene Punkte / bewusste Entscheidungen

- **Videountertitel (`<track>`):** Die Demo-Videos haben **keinen Ton**. Statt
  WebVTT-Untertiteln gibt es eine gleichwertige **Textbeschreibung** direkt unter
  jedem Video. Damit ist der Inhalt auch ohne Abspielen vollständig erfassbar.
- **Video-Poster:** Aktuell `preload="metadata"` (erstes Frame als Vorschau). Ein
  dediziertes Poster-Bild kann über das optionale `video_poster`-Feld pro Karte
  ergänzt werden.
- **Kontrast-Verifikation:** Werte rechnerisch gegen Weiß geprüft; für die
  Endabnahme empfiehlt sich ein Lauf mit axe DevTools oder Lighthouse auf der
  gerenderten Seite.

## Prüfung wiederholen

Nach Änderungen am Layout oder an den Farben:

1. Seite lokal bauen (`bundle exec jekyll serve`).
2. Lighthouse-Accessibility-Audit oder axe DevTools laufen lassen.
3. Einmal komplett per Tastatur durchtabben (Skip-Link → Inhalt → Formular → Footer).
