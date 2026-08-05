#!/usr/bin/env python3
"""Bewerbungs-Builder: ein Befehl, ein Browserfenster, fertiges PDF.

    python scripts/bewerbung.py

Startet einen kleinen Server auf 127.0.0.1 (nur lokal erreichbar), oeffnet die
Auswahlseite im Browser und nimmt die fertige Bewerbung direkt entgegen: die
Seite schickt sie als JSON, der Server legt sie als YAML in bewerbungen/ ab,
baut daraus das PDF (ueber generate_application.py) und oeffnet es.

Die YAML-Datei bleibt liegen — das Anschreiben laesst sich dort im Editor
weiterschreiben und mit generate_application.py neu bauen, ohne die Auswahl
erneut zusammenzuklicken.
"""

import html
import http.server
import json
import os
import re
import subprocess
import threading
import webbrowser

import yaml

from generate_application import Abbruch, build_pdf, load_yaml
from generate_cv import ROOT

BEWERBUNGEN = os.path.join(ROOT, "bewerbungen")
UMLAUTE = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})


def slug(value):
    """Dateinamen-Baustein aus freiem Text. Bewusst streng: der Wert kommt aus
    dem Browser und darf niemals aus bewerbungen/ herausfuehren."""
    value = (value or "").lower().translate(UMLAUTE)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:60] or "bewerbung"


def dump_yaml(data):
    """YAML mit Block-Scalars fuer mehrzeiligen Text — das Anschreiben soll in
    der Datei lesbar und von Hand editierbar bleiben."""
    class Dumper(yaml.SafeDumper):
        pass

    def represent_str(dumper, value):
        style = "|" if "\n" in value else None
        return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)

    Dumper.add_representer(str, represent_str)
    return yaml.dump(data, Dumper=Dumper, allow_unicode=True, sort_keys=False,
                     default_flow_style=False, width=100)


def sections_for_page():
    """Sektionen und Eintraege aus content.yml — ohne die Kontakt-Sektion."""
    content = load_yaml(os.path.join(ROOT, "_data", "content.yml"), "content.yml")
    out = []
    for section in content.get("sections", []):
        if section.get("form_endpoint") or not section.get("cards"):
            continue
        cards = []
        for card in section["cards"]:
            label = card["role"]
            if card.get("organization"):
                label += f' — {card["organization"]}'
            cards.append({"id": card["id"], "label": label})
        out.append({"id": section["id"], "title": section["title"], "cards": cards})
    return out


def build_from_request(payload):
    """Bewerbung als YAML ablegen und PDF bauen. Gibt (yaml_pfad, pdf_pfad,
    anzahl_sektionen) zurueck."""
    application = {
        "empfaenger": payload.get("empfaenger") or {},
        "datum": payload.get("datum", ""),
        "betreff": payload.get("betreff", ""),
        "anrede": payload.get("anrede", ""),
        "anschreiben": payload.get("anschreiben", ""),
        "gruss": payload.get("gruss", ""),
        "sections": payload.get("sections") or [],
    }

    os.makedirs(BEWERBUNGEN, exist_ok=True)
    name = "bewerbung-" + slug(application["empfaenger"].get("firma"))
    yaml_path = os.path.join(BEWERBUNGEN, name + ".yml")
    pdf_path = os.path.join(BEWERBUNGEN, name + ".pdf")

    count = build_pdf(application, pdf_path)  # zuerst bauen: schlaegt es fehl,
    with open(yaml_path, "w", encoding="utf-8") as f:  # bleibt nichts Halbes liegen
        f.write("# Erzeugt mit scripts/bewerbung.py. Aenderungen hier wirken beim\n"
                "# naechsten Lauf von: python scripts/generate_application.py <diese Datei>\n")
        f.write(dump_yaml(application))
    return yaml_path, pdf_path, count


def render_page():
    esc = lambda v: html.escape(str(v), quote=True)
    blocks = []
    for section in sections_for_page():
        title = esc(section["title"])
        items = "".join(
            f'<li><input type="checkbox" id="card-{card["id"]}" value="{card["id"]}" checked>'
            f'<label for="card-{card["id"]}">{esc(card["label"])}</label></li>'
            for card in section["cards"]
        )
        blocks.append(f"""<fieldset class="section" data-id="{section["id"]}" data-title="{title}">
  <legend>{title}</legend>
  <div class="tools">
    <button type="button" data-move="up" aria-label="{title}: nach oben">nach oben</button>
    <button type="button" data-move="down" aria-label="{title}: nach unten">nach unten</button>
    <button type="button" data-all="on" aria-label="{title}: alle auswählen">alle</button>
    <button type="button" data-all="off" aria-label="{title}: keine auswählen">keine</button>
  </div>
  <ul class="cards">{items}</ul>
</fieldset>""")

    return PAGE.replace("<!--SEKTIONEN-->", "\n".join(blocks))


PAGE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bewerbung zusammenstellen</title>
<style>
  body { font-family: "Open Sans", -apple-system, sans-serif; color: #24292e;
         line-height: 1.5; max-width: 50rem; margin: 0 auto; padding: 2rem 1rem 4rem; }
  h1 { color: #0b6b3a; font-size: 1.8rem; margin: 0 0 0.3rem; }
  h2 { color: #0b6b3a; font-size: 1.2rem; margin: 2rem 0 0.5rem;
       border-bottom: 1px solid #e1e4e8; padding-bottom: 0.3rem; }
  .lead { color: #586069; margin: 0 0 1rem; }
  .fields { display: flex; flex-direction: column; gap: 0.5rem; }
  .fields label { font-size: 0.9rem; color: #444d56; font-weight: 600; }
  input, textarea { font: inherit; font-size: 0.95rem; padding: 0.5rem 0.75rem;
                    border: 1px solid #d0d7de; border-radius: 4px; color: #24292e; }
  fieldset { border: 1px solid #e1e4e8; border-radius: 6px; padding: 0.75rem 1rem 1rem;
             margin: 0 0 1rem; }
  legend { font-weight: 700; color: #0b6b3a; padding: 0 0.4rem; }
  .tools { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 0.6rem; }
  .tools button { font: inherit; font-size: 0.8rem; padding: 0.25rem 0.6rem; background: #fff;
                  border: 1px solid #d0d7de; border-radius: 4px; cursor: pointer; }
  .tools button:hover { background: #f3f6f9; }
  .cards { list-style: none; margin: 0; padding: 0; }
  .cards li { display: flex; gap: 0.5rem; align-items: baseline; margin: 0.2rem 0; }
  .cards label { font-size: 0.9rem; }
  .hint { font-size: 0.85rem; color: #586069; }
  #bauen { font: inherit; font-size: 1rem; padding: 0.7rem 1.6rem; background: #0066cc;
           color: #fff; border: none; border-radius: 4px; cursor: pointer; }
  #bauen:hover { background: #0052a3; }
  #bauen:disabled { background: #8ab4d8; cursor: not-allowed; }
  #status { margin-top: 0.8rem; font-size: 0.95rem; }
  #status:empty { display: none; }
  #status.ok { color: #1a7f37; }
  #status.fehler { color: #cf222e; white-space: pre-wrap; }
  a:focus-visible, button:focus-visible, input:focus-visible, textarea:focus-visible {
    outline: 3px solid #0b5c5c; outline-offset: 2px; }
</style>
</head>
<body>
<h1>Bewerbung zusammenstellen</h1>
<p class="lead">Anschreiben schreiben, passende Einträge auswählen, PDF erzeugen.</p>

<h2>Anschreiben</h2>
<div class="fields">
  <label for="firma">Firma</label>
  <input type="text" id="firma" placeholder="Muster GmbH">
  <label for="person">Ansprechpartner:in (optional)</label>
  <input type="text" id="person" placeholder="Frau Dr. Muster">
  <label for="strasse">Straße (optional)</label>
  <input type="text" id="strasse" placeholder="Musterweg 1">
  <label for="ort">PLZ und Ort (optional)</label>
  <input type="text" id="ort" placeholder="69117 Heidelberg">
  <label for="datum">Datum</label>
  <input type="text" id="datum">
  <label for="betreff">Betreff</label>
  <input type="text" id="betreff" placeholder="Bewerbung als …">
  <label for="anrede">Anrede</label>
  <input type="text" id="anrede" value="Sehr geehrte Damen und Herren,">
  <label for="anschreiben">Anschreiben</label>
  <textarea id="anschreiben" rows="14" placeholder="Absätze durch eine Leerzeile trennen."></textarea>
  <label for="gruss">Grußformel</label>
  <input type="text" id="gruss" value="Mit freundlichen Grüßen">
</div>

<h2>Inhalte auswählen</h2>
<p class="hint">Abgewählte Einträge erscheinen nicht im PDF. Sektionen ohne ausgewählten
Eintrag fallen ganz weg. „nach oben“/„nach unten“ ändert die Reihenfolge im PDF.</p>
<div id="sektionen"><!--SEKTIONEN--></div>
<p class="hint" id="reihenfolge" aria-live="polite"></p>

<h2>PDF erzeugen</h2>
<button type="button" id="bauen">PDF erzeugen und öffnen</button>
<p id="status" role="status" aria-live="polite"></p>

<script>
  var list = document.getElementById('sektionen');
  var reihenfolge = document.getElementById('reihenfolge');
  var status = document.getElementById('status');
  var button = document.getElementById('bauen');

  document.getElementById('datum').value = new Date().toLocaleDateString('de-DE', {
    day: 'numeric', month: 'long', year: 'numeric'
  });

  list.addEventListener('click', function (event) {
    var clicked = event.target.closest('button');
    if (!clicked) return;
    var section = clicked.closest('.section');

    if (clicked.dataset.all) {
      var on = clicked.dataset.all === 'on';
      section.querySelectorAll('input').forEach(function (box) { box.checked = on; });
      return;
    }

    var up = clicked.dataset.move === 'up';
    var sibling = up ? section.previousElementSibling : section.nextElementSibling;
    if (!sibling) {
      reihenfolge.textContent = section.dataset.title + ' steht bereits ' +
        (up ? 'an erster' : 'an letzter') + ' Stelle.';
      return;
    }
    if (up) { list.insertBefore(section, sibling); } else { list.insertBefore(sibling, section); }
    // Nach dem Umhaengen ist der Fokus weg — zurueck auf denselben Button, sonst
    // laesst sich per Tastatur nicht mehrfach hintereinander schieben.
    clicked.focus();
    reihenfolge.textContent = section.dataset.title + ' ist jetzt an Position ' +
      (Array.prototype.indexOf.call(list.children, section) + 1) + ' von ' + list.children.length + '.';
  });

  function wert(id) { return document.getElementById(id).value.trim(); }

  button.addEventListener('click', function () {
    var sections = [];
    Array.prototype.forEach.call(list.children, function (section) {
      var cards = Array.prototype.filter.call(section.querySelectorAll('input'), function (box) {
        return box.checked;
      }).map(function (box) { return box.value; });
      if (cards.length) sections.push({ id: section.dataset.id, cards: cards });
    });

    if (!sections.length) {
      status.className = 'fehler';
      status.textContent = 'Kein Eintrag ausgewählt — bitte mindestens einen auswählen.';
      return;
    }

    status.className = '';
    status.textContent = 'PDF wird gebaut …';
    button.disabled = true;

    fetch('/erzeugen', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        empfaenger: { firma: wert('firma'), person: wert('person'),
                      strasse: wert('strasse'), ort: wert('ort') },
        datum: wert('datum'),
        betreff: wert('betreff'),
        anrede: wert('anrede'),
        anschreiben: document.getElementById('anschreiben').value,
        gruss: wert('gruss'),
        sections: sections
      })
    }).then(function (antwort) {
      return antwort.json().then(function (daten) {
        if (!antwort.ok) throw new Error(daten.fehler || 'Unbekannter Fehler');
        status.className = 'ok';
        status.textContent = 'Fertig: ' + daten.pdf + ' (' + daten.sektionen +
          ' Sektionen). Das PDF öffnet sich. Die Datei ' + daten.yaml +
          ' bleibt zum Nachbearbeiten liegen.';
      });
    }).catch(function (error) {
      status.className = 'fehler';
      status.textContent = error.message;
    }).finally(function () {
      button.disabled = false;
    });
  });
</script>
</body>
</html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    def antworte(self, code, typ, body):
        self.send_response(code)
        self.send_header("Content-Type", typ)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != "/":
            self.antworte(404, "text/plain; charset=utf-8", b"Nicht gefunden")
            return
        self.antworte(200, "text/html; charset=utf-8", render_page().encode("utf-8"))

    def do_POST(self):
        if self.path != "/erzeugen":
            self.antworte(404, "text/plain; charset=utf-8", b"Nicht gefunden")
            return

        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length))
        try:
            yaml_path, pdf_path, count = build_from_request(payload)
        except Abbruch as error:
            self.antworte(400, "application/json",
                          json.dumps({"fehler": str(error)}).encode("utf-8"))
            print(f"  Abbruch: {error}")
            return

        subprocess.run(["open", pdf_path], check=False)
        relative = lambda p: os.path.relpath(p, ROOT)
        print(f"  Gebaut: {relative(pdf_path)} ({count} Sektionen)")
        self.antworte(200, "application/json", json.dumps({
            "pdf": relative(pdf_path), "yaml": relative(yaml_path), "sektionen": count,
        }).encode("utf-8"))

    def log_message(self, *args):
        pass  # der Server soll nur melden, was gebaut wurde


def main():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    url = f"http://127.0.0.1:{server.server_port}/"
    print(f"Bewerbungs-Builder laeuft: {url}\nZum Beenden: Strg+C", flush=True)
    threading.Timer(0.5, webbrowser.open, [url]).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBeendet.")


if __name__ == "__main__":
    main()
