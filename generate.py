#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera il repository Kodi per Burlesco (hosting su GitHub Pages).

Output TUTTO nella sottocartella `public/` (che la CI pubblica su gh-pages):
  public/
    ├── index.html
    ├── addons.xml              (indice del repository)
    ├── addons.xml.md5          (checksum)
    ├── repository.burlesco/repository.burlesco-<v>.zip
    └── plugin.video.castellano/plugin.video.castellano-<v>.zip

La cartella `public/` NON contiene un .gitignore, quindi il workflow pubblica
tutti i file (zips + addons.xml) senza escluderli.

Uso:  python generate.py
"""

import hashlib
import os
import re
import shutil
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'public')

# Add-on da includere nel repository (ordine di elenco)
ADDONS = ['repository.burlesco', 'plugin.video.castellano']

EXCLUDE_DIRS = {'__pycache__', '.git', '.github', 'public'}
EXCLUDE_FILES = {'.gitignore', 'Thumbs.db', '.DS_Store', 'config.json'}


def read_version(addon_dir):
    with open(os.path.join(ROOT, addon_dir, 'addon.xml'), encoding='utf-8') as f:
        data = f.read()
    m = re.search(r'<addon\b[^>]*\bversion="([^"]+)"', data)
    if not m:
        sys.exit('Versione non trovata in %s/addon.xml' % addon_dir)
    return m.group(1)


def addon_element(addon_dir):
    with open(os.path.join(ROOT, addon_dir, 'addon.xml'), encoding='utf-8') as f:
        data = f.read()
    data = re.sub(r'<\?xml[^>]*\?>', '', data).strip()
    m = re.search(r'<addon\b.*?</addon>', data, re.S)
    if not m:
        sys.exit('Elemento <addon> non trovato in %s/addon.xml' % addon_dir)
    return m.group(0)


def make_zip(addon_dir, version):
    """Crea public/<id>/<id>-<version>.zip escludendo cache/file di build."""
    addon_id = os.path.basename(addon_dir)
    base = os.path.join(ROOT, addon_dir)
    out_dir = os.path.join(OUT, addon_id)
    os.makedirs(out_dir, exist_ok=True)
    out_zip = os.path.join(out_dir, '%s-%s.zip' % (addon_id, version))
    if os.path.exists(out_zip):
        os.remove(out_zip)
    count = 0
    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for name in files:
                if name in EXCLUDE_FILES or name.endswith(('.pyc', '.pyo', '.zip')):
                    continue
                full = os.path.join(root, name)
                rel = os.path.relpath(full, base)
                arc = '%s/%s' % (addon_id, rel.replace('\\', '/'))
                z.write(full, arc)
                count += 1
    return count


def main():
    # pulisci e ricrea la cartella di output
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    # pagina di benvenuto (se presente nella root)
    idx_src = os.path.join(ROOT, 'index.html')
    repo_zip_name = None
    if os.path.isfile(idx_src):
        shutil.copy(idx_src, os.path.join(OUT, 'index.html'))

    elements = []
    for addon_dir in ADDONS:
        version = read_version(addon_dir)
        count = make_zip(addon_dir, version)
        elements.append(addon_element(addon_dir))
        zname = '%s-%s.zip' % (addon_dir, version)
        if addon_dir == 'repository.burlesco':
            repo_zip_name = zname
        print('  %-28s v%s  (%d file)' % (addon_dir, version, count))

    # copia lo zip del repository anche alla radice: cosi' l'utente lo vede
    # navigando la sorgente in "Installa da file ZIP" (GitHub Pages non ha
    # la lista cartelle, Kodi legge i link dall'index.html).
    if repo_zip_name:
        shutil.copy(
            os.path.join(OUT, 'repository.burlesco', repo_zip_name),
            os.path.join(OUT, repo_zip_name),
        )

    addons_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<addons>\n' + '\n'.join(elements) + '\n</addons>\n'
    )
    with open(os.path.join(OUT, 'addons.xml'), 'w', encoding='utf-8') as f:
        f.write(addons_xml)
    md5 = hashlib.md5(addons_xml.encode('utf-8')).hexdigest()
    with open(os.path.join(OUT, 'addons.xml.md5'), 'w') as f:
        f.write(md5)

    print('Generato in public/: addons.xml (md5=%s) + zip' % md5)


if __name__ == '__main__':
    main()