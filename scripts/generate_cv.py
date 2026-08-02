#!/usr/bin/env python3
"""Erzeugt das CV-PDF aus _data/content.yml — als getaggtes PDF/UA-1.

Frueher lief die Erzeugung ueber LaTeX (moderncv/XeLaTeX). LaTeX produziert
aber untagged PDFs (keine Struktur, keine Lesereihenfolge, kein /Lang) und ist
damit nicht barrierefrei. Dieser Weg baut stattdessen semantisches HTML aus
derselben Datenquelle und rendert es mit WeasyPrint zu einem getaggten,
sprachlich ausgezeichneten PDF/UA-1-Dokument.
"""

import html
import os

import yaml
from weasyprint import HTML

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTO = "assets/images/profile.jpg"


def esc(text):
    return html.escape(str(text)) if text else ""


def link(url, label):
    return f'<a href="{esc(url)}">{esc(label)}</a>'


def render_card(card):
    """Eine Karte als <article>. Deckt Projekte (Problem/Loesung/...),
    Erfahrungs-/Ausbildungseintraege (role/org/date/description) ab."""
    # Projekte an ihren Feldern erkennen, nicht am Sektionstitel: eine
    # Umbenennung der Sektion soll die Auszeichnung nicht stillschweigend brechen.
    is_project = any(card.get(k) for k in ("problem", "solution", "result"))
    parts = [f'<article class="entry{" project" if is_project else ""}">']
    parts.append(f'<h3>{esc(card.get("role", ""))}</h3>')

    meta = []
    if card.get("organization"):
        meta.append(esc(card["organization"]))
    if card.get("date"):
        meta.append(esc(card["date"]))
    if meta:
        parts.append(f'<p class="meta">{" · ".join(meta)}</p>')

    if card.get("description"):
        parts.append(f'<p>{esc(card["description"])}</p>')

    if card.get("bullets"):
        items = "".join(f"<li>{esc(b)}</li>" for b in card["bullets"])
        parts.append(f"<ul>{items}</ul>")

    for key, lbl in (("problem", "Problem"), ("solution", "Lösung"),
                     ("result", "Ergebnis"), ("stack", "Stack")):
        if card.get(key):
            parts.append(f'<p><strong>{lbl}:</strong> {esc(card[key])}</p>')

    if card.get("links"):
        hrefs = " · ".join(link(l.get("url", ""), l.get("label", "")) for l in card["links"])
        parts.append(f'<p class="links">{hrefs}</p>')

    parts.append("</article>")
    return "\n".join(parts)


def is_list_section(cards):
    """Reine Aufzaehlungen (nur role, evtl. org) -> als <ul> rendern."""
    for c in cards:
        if any(c.get(k) for k in ("date", "description", "bullets", "problem",
                                  "solution", "result", "stack", "links")):
            return False
    return True


def render_section(section):
    if section.get("form_endpoint"):
        return ""  # Kontaktformular gehoert nicht ins PDF
    out = ['<section>']
    out.append(f'<h2>{esc(section.get("title", ""))}</h2>')
    if section.get("text"):
        out.append(f'<p>{esc(section["text"])}</p>')

    cards = section.get("cards")
    if cards:
        if is_list_section(cards):
            out.append("<ul>")
            for c in cards:
                role = esc(c.get("role", ""))
                if c.get("organization"):
                    role += f' — {esc(c["organization"])}'
                out.append(f"<li>{role}</li>")
            out.append("</ul>")
        else:
            for c in cards:
                out.append(render_card(c))
    out.append("</section>")
    return "\n".join(out)


def build_html(content):
    name = esc(content["name"])
    subtitle = esc(content.get("subtitle", ""))

    contact = []
    if content.get("location"):
        contact.append(esc(content["location"]))
    if content.get("email"):
        contact.append(link(f'mailto:{content["email"]}', content["email"]))
    if content.get("linkedin"):
        contact.append(link(f'https://www.linkedin.com/in/{content["linkedin"]}', "LinkedIn"))
    if content.get("github"):
        contact.append(link(f'https://github.com/{content["github"]}', "GitHub"))
    contact_line = " · ".join(contact)

    # Intro als "Profil"-Abschnitt (mehrere Absaetze -> je ein <p>)
    profil = ""
    if content.get("intro"):
        paras = "".join(f"<p>{esc(p.strip())}</p>"
                        for p in content["intro"].split("\n\n") if p.strip())
        profil = f"<section><h2>Profil</h2>{paras}</section>"

    sections = "\n".join(render_section(s) for s in content.get("sections", []))

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>Lebenslauf – {name}</title>
<meta name="author" content="{name}">
<meta name="description" content="{subtitle}">
<style>{CSS}</style>
</head>
<body>
<header class="cv-header">
  <img class="photo" src="{PHOTO}" alt="Profilfoto von {name}">
  <div class="ident">
    <h1>{name}</h1>
    <p class="subtitle">{subtitle}</p>
    <p class="contact">{contact_line}</p>
  </div>
</header>
<main>
{profil}
{sections}
</main>
</body>
</html>"""


CSS = """
@page {
  size: A4;
  margin: 1.6cm 1.7cm;
}
* { box-sizing: border-box; }
body {
  font-family: "Helvetica Neue", "Arial", "DejaVu Sans", sans-serif;
  font-size: 10.5pt;
  line-height: 1.45;
  color: #1c1c1c;
  margin: 0;
}
a { color: #0a5ca8; text-decoration: none; }
.cv-header {
  display: flex;
  align-items: center;
  gap: 1.1cm;
  border-bottom: 2px solid #0b6b3a;
  padding-bottom: 0.5cm;
  margin-bottom: 0.5cm;
}
.photo {
  width: 2.6cm; height: 2.6cm;
  border-radius: 50%; object-fit: cover;
  flex-shrink: 0;
}
h1 { font-size: 20pt; margin: 0; color: #0b6b3a; }
.subtitle { font-size: 11pt; font-weight: 600; margin: 0.15cm 0 0; color: #1c1c1c; }
.contact { font-size: 9pt; margin: 0.2cm 0 0; color: #444; }
h2 {
  font-size: 12.5pt; color: #0b6b3a;
  border-bottom: 1px solid #d0d7de;
  padding-bottom: 0.1cm; margin: 0.55cm 0 0.25cm;
}
h3 { font-size: 10.5pt; margin: 0.35cm 0 0.05cm; color: #1c1c1c; }
/* Nur Projekttitel gruen; Stationen und Abschluesse bleiben dunkel. */
.project h3 { color: #0b6b3a; }
.entry { margin-bottom: 0.25cm; }
.entry p { margin: 0.06cm 0; }
.meta { font-size: 9pt; color: #555; }
.links { font-size: 9pt; }
ul { margin: 0.1cm 0; padding-left: 0.6cm; }
li { margin: 0.05cm 0; }
section { page-break-inside: auto; }
h2, h3 { break-after: avoid; }
"""


def main():
    with open(os.path.join(ROOT, "_data", "content.yml"), encoding="utf-8") as f:
        content = yaml.safe_load(f)
    doc = build_html(content)
    out = os.path.join(ROOT, "cv.pdf")
    HTML(string=doc, base_url=ROOT).write_pdf(out, pdf_variant="pdf/ua-1")
    print(f"Generated {out} (PDF/UA-1, getaggt)")


if __name__ == "__main__":
    main()
