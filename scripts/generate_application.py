#!/usr/bin/env python3
"""Erzeugt aus einer Bewerbungsdatei ein PDF: Anschreiben + kuratiertes Kurzprofil.

Die Auswahl entsteht in scripts/bewerbung.py und verweist per `id` auf Sektionen
und Eintraege in _data/content.yml. Dieses Skript baut die abgelegte YAML-Datei
erneut, wenn du das Anschreiben von Hand nachbearbeitet hast. Gerendert wird wie
beim CV-PDF mit WeasyPrint als getaggtes PDF/UA-1; Sektionsaufbau und Layout
kommen aus generate_cv.py, damit beide Dokumente gleich aussehen.

    python scripts/generate_application.py bewerbungen/musterfirma.yml
"""

import os
import sys

import yaml
from weasyprint import HTML

from generate_cv import CSS, PHOTO, ROOT, esc, link, render_section

SENDER_FILE = os.path.join(ROOT, "bewerbungen", "absender.yml")
SENDER_FIELDS = ("strasse", "ort")


class Abbruch(Exception):
    """Erwarteter Abbruch mit Klartextmeldung. Der Server (bewerbung.py) faengt
    sie ab und zeigt sie im Browser, statt sich zu beenden."""


def fail(message):
    raise Abbruch(message)


def load_yaml(path, what):
    if not os.path.exists(path):
        fail(f"{what} nicht gefunden: {path}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_sender():
    if not os.path.exists(SENDER_FILE):
        fail(
            f"Absenderdaten fehlen: {SENDER_FILE}\n"
            f"  Vorlage kopieren: cp scripts/absender.example.yml {SENDER_FILE}\n"
            f"  Erwartete Felder: {', '.join(SENDER_FIELDS)} (telefon optional)"
        )
    sender = load_yaml(SENDER_FILE, "Absenderdatei")
    missing = [f for f in SENDER_FIELDS if not sender.get(f)]
    if missing:
        fail(f"In {SENDER_FILE} fehlen die Felder: {', '.join(missing)}")
    return sender


def index_content(content):
    """{sektion_id: (sektion, {karten_id: karte})} — bricht ab, wenn ids fehlen."""
    index = {}
    for section in content.get("sections", []):
        section_id = section.get("id")
        if not section_id:
            fail(f'Sektion ohne id in content.yml: "{section.get("title", "?")}"')
        cards = {}
        for card in section.get("cards") or []:
            card_id = card.get("id")
            if not card_id:
                fail(f'Eintrag ohne id in content.yml: "{card.get("role", "?")}"')
            cards[card_id] = card
        index[section_id] = (section, cards)
    return index


def select_sections(application, index):
    """Sektionen in der Reihenfolge der Bewerbungsdatei, auf die gewaehlten
    Eintraege gefiltert. Unbekannte ids sind ein Fehler — sonst faellt ein
    Eintrag stillschweigend aus der Bewerbung."""
    selected = []
    for entry in application.get("sections") or []:
        section_id = entry.get("id")
        if section_id not in index:
            fail(f"Unbekannte Sektions-id: {section_id}")
        section, cards = index[section_id]
        picked = []
        for card_id in entry.get("cards") or []:
            if card_id not in cards:
                fail(f"Unbekannte Eintrags-id in Sektion {section_id}: {card_id}")
            picked.append(cards[card_id])
        if picked:
            selected.append({"title": section.get("title", ""), "cards": picked})
    if not selected:
        fail("Die Bewerbungsdatei waehlt keinen einzigen Eintrag aus.")
    return selected


def render_address(lines, css_class):
    kept = [esc(l) for l in lines if l]
    return f'<address class="{css_class}">{"<br>".join(kept)}</address>'


def render_letter(application, content, sender):
    recipient = application.get("empfaenger") or {}
    subject = application.get("betreff") or "Bewerbung"

    sender_block = render_address([
        content["name"],
        sender.get("strasse"),
        sender.get("ort"),
        sender.get("telefon"),
        content.get("email"),
    ], "sender")

    recipient_block = render_address([
        recipient.get("firma"),
        recipient.get("person"),
        recipient.get("strasse"),
        recipient.get("ort"),
    ], "recipient")

    body = "".join(
        f"<p>{esc(p.strip())}</p>"
        for p in (application.get("anschreiben") or "").split("\n\n")
        if p.strip()
    )

    # Leere Felder ganz weglassen: ein leeres <p> waere im Strukturbaum ein
    # inhaltsloser Absatz, den Screenreader trotzdem ansagen.
    date = f'<p class="date">{esc(application["datum"])}</p>' if application.get("datum") else ""
    salutation = f'<p>{esc(application["anrede"])}</p>' if application.get("anrede") else ""
    closing = ""
    if application.get("gruss"):
        closing = (f'<p class="closing">{esc(application["gruss"])}<br><br>'
                   f'{esc(content["name"])}</p>')

    return f"""<section class="letter">
{sender_block}
{recipient_block}
{date}
<h1 class="subject">{esc(subject)}</h1>
{salutation}
{body}
{closing}
</section>"""


def build_html(application, content, sender, sections):
    name = esc(content["name"])
    subtitle = esc(content.get("subtitle", ""))
    subject = esc(application.get("betreff") or "Bewerbung")

    contact = []
    if content.get("email"):
        contact.append(link(f'mailto:{content["email"]}', content["email"]))
    if content.get("linkedin"):
        contact.append(link(f'https://www.linkedin.com/in/{content["linkedin"]}', "LinkedIn"))
    if content.get("github"):
        contact.append(link(f'https://github.com/{content["github"]}', "GitHub"))

    body = "\n".join(render_section(s) for s in sections)

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>{subject} – {name}</title>
<meta name="author" content="{name}">
<meta name="description" content="{subject}">
<style>{CSS}{LETTER_CSS}</style>
</head>
<body>
<main>
{render_letter(application, content, sender)}
<header class="cv-header">
  <img class="photo" src="{PHOTO}" alt="Profilfoto von {name}">
  <div class="ident">
    <p class="ident-name">{name}</p>
    <p class="subtitle">{subtitle}</p>
    <p class="contact">{" · ".join(contact)}</p>
  </div>
</header>
{body}
</main>
</body>
</html>"""


# Ergaenzt das aus generate_cv.py importierte CSS um die Briefseite. Die
# Profilseite nutzt unveraendert die dortigen Klassen, damit beide PDFs gleich
# aussehen.
LETTER_CSS = """
.letter { page-break-after: always; }
.letter address { font-style: normal; }
.letter .sender { text-align: right; font-size: 9pt; color: #444; margin-bottom: 1.4cm; }
.letter .recipient { margin-bottom: 1.2cm; line-height: 1.4; }
.letter .date { text-align: right; margin: 0 0 0.9cm; }
h1.subject { font-size: 12.5pt; margin: 0 0 0.6cm; }
.letter p { margin: 0 0 0.35cm; }
.letter .closing { margin-top: 0.9cm; }
.ident-name { font-size: 20pt; font-weight: 700; margin: 0; color: #0b6b3a; }
"""


def build_pdf(application, out):
    """Baut das PDF und gibt die Zahl der aufgenommenen Sektionen zurueck."""
    content = load_yaml(os.path.join(ROOT, "_data", "content.yml"), "content.yml")
    sender = load_sender()
    sections = select_sections(application, index_content(content))
    doc = build_html(application, content, sender, sections)
    HTML(string=doc, base_url=ROOT).write_pdf(out, pdf_variant="pdf/ua-1")
    return len(sections)


def main():
    if len(sys.argv) < 2:
        sys.exit("Aufruf: python scripts/generate_application.py <bewerbung.yml> [ausgabe.pdf]")

    source = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(source)[0] + ".pdf"
    try:
        count = build_pdf(load_yaml(source, "Bewerbungsdatei"), out)
    except Abbruch as error:
        sys.exit(f"Abbruch: {error}")
    print(f"Generated {out} (PDF/UA-1, getaggt) — {count} Sektionen")


if __name__ == "__main__":
    main()
