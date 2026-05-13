import yaml
import re
import os

def escape(text):
    if not text:
        return ""
    def replace(m):
        return {
            '\\': r'\textbackslash{}',
            '{': r'\{', '}': r'\}',
            '&': r'\&', '%': r'\%',
            '$': r'\$', '#': r'\#',
            '_': r'\_', '^': r'\^{}',
            '~': r'\textasciitilde{}',
        }[m.group(0)]
    return re.sub(r'[\\{}&%$#_^~]', replace, str(text))

def generate(content):
    parts = content['name'].split(' ', 1)
    first = escape(parts[0])
    last  = escape(parts[1] if len(parts) > 1 else '')

    lines = [
        r'\documentclass[11pt,a4paper]{moderncv}',
        r'\moderncvstyle{classic}',
        r'\moderncvcolor{blue}',
        r'\usepackage[ngerman]{babel}',
        r'\usepackage[scale=0.80]{geometry}',
        '',
        f'\\name{{{first}}}{{{last}}}',
        f'\\title{{{escape(content.get("subtitle", ""))}}}',
        f'\\address{{{escape(content.get("location", ""))}}}{{}}{{}}',
        r'\email{a.eckerlin@gmx.de}',
        r'\social[linkedin]{alexander-eckerlin}',
        r'\social[github]{ecklex}',
        r'\photo[96pt][0.4pt]{assets/images/profile}',
        '',
        r'\begin{document}',
        r'\makecvtitle',
        '',
    ]

    for section in content.get('sections', []):
        if section.get('form_endpoint'):
            continue

        lines.append(f'\\section{{{escape(section.get("title", ""))}}}')

        if section.get('text'):
            lines.append(f'\\cvitem{{}}{{\\small {escape(section["text"])}}}')
            lines.append('')

        if section.get('type') == 'cards':
            for card in section.get('cards', []):
                role = escape(card.get('role', ''))
                org  = escape(card.get('organization', ''))
                date = escape(card.get('date', ''))
                desc = escape(card.get('description', ''))

                if date:
                    lines.append(f'\\cventry{{{date}}}{{{role}}}{{{org}}}{{}}{{}}{{\\small {desc}}}')
                elif org:
                    lines.append(f'\\cvitem{{{role}}}{{{org}}}')
                elif desc or card.get('links'):
                    links_str = ''
                    if card.get('links'):
                        labels = [escape(l.get('label', '')) for l in card['links']]
                        links_str = ' \\textbar{} '.join(labels)
                    extra = f' \\textit{{({links_str})}}' if links_str else ''
                    lines.append(f'\\cventry{{}}{{{role}}}{{}}{{}}{{}}{{\\small {desc}{extra}}}')
                else:
                    lines.append(f'\\cvlistitem{{{role}}}')

        if section.get('items'):
            for item in section['items']:
                lines.append(f'\\cvlistitem{{{escape(item)}}}')

        lines.append('')

    lines.append(r'\end{document}')
    return '\n'.join(lines)

if __name__ == '__main__':
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(root, '_data', 'content.yml'), encoding='utf-8') as f:
        content = yaml.safe_load(f)
    tex = generate(content)
    out = os.path.join(root, 'cv.tex')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(tex)
    print(f'Generated {out}')
