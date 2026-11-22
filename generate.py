#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera il repository Kodi per Burlesco (hosting su GitHub Pages).

Per ogni add-on:
  1. crea lo zip <id>/<id>-<versione>.zip (struttura con <datadir zip="true">)
  2. legge addon.xml per comporre addons.xml (indice del repository)
  3. scrive addons.xml.md5 (checksum)

Uso:  python generate.py
Output (nella root del repo burlesco):
  addons.xml, addons.xml.md5
  <id>/<id>-<versione>.zip  per ogni add-on
"""

import hashlib
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))

# Add-on da includere nel repository (ordine di elenco)
ADDONS = ['repository.burlesco', 'plugin.video.castellano']

EXCLUDE_DIRS = {'__pycache__', '.git', '.github'}
EXCLUDE_FILES = {'.gitignore', 'Thumbs.db', '.DS_Store', 'config.json'}


def read_version(addon_dir):
    with open(os.path.join(ROOT, addon_dir, 'addon.xml'), encoding='utf-8') as f:
        data = f.read()
    m = re.search(r'<addon\b[^>]*\bversion="([^"]+)"', data)
    if not m:
        sys.exit('Versione non trovata in %s/addon.xml' % addon_dir)
    return m.group(1)


def addon_element(addon_dir):
    """Restituisce l'elemento <addon>...</addon> senza dichiarazione XML."""
    with open(os.path.join(ROOT, addon_dir, 'addon.xml'), encoding='utf-8') as f:
        data = f.read()
    data = re.sub(r'<\?xml[^>]*\?>', '', data).strip()
    m = re.search(r'<addon\b.*?</addon>', data, re.S)
    if not m:
        sys.exit('Elemento <addon> non trovato in %s/addon.xml' % addon_dir)
    return m.group(0)


def make_zip(addon_dir, version):
    """Crea <addon_dir>/<id>-<version>.zip escludendo file di build/cache."""
    addon_id = os.path.basename(addon_dir)
    base = os.path.join(ROOT, addon_dir)
    out_zip = os.path.join(base, '%s-%s.zip' % (addon_id, version))
    if os.path.exists(out_zip):
        os.remove(out_zip)
    count = 0
    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for name in files:
                if name in EXCLUDE_FILES or name.endswith(('.pyc', '.pyo')):
                    continue
                # non includere lo zip che stiamo creando
                if name.endswith('.zip'):
                    continue
                full = os.path.join(root, name)
                rel = os.path.relpath(full, base)
                arc = '%s/%s' % (addon_id, rel.replace('\\', '/'))
                z.write(full, arc)
                count += 1
    return out_zip, count


def main():
    elements = []
    for addon_dir in ADDONS:
        version = read_version(addon_dir)
        zip_path, count = make_zip(addon_dir, version)
        elements.append(addon_element(addon_dir))
        print('  %-28s v%s  (%d file)' % (addon_dir, version, count))

    addons_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<addons>\n' + '\n'.join(elements) + '\n</addons>\n'
    )
    with open(os.path.join(ROOT, 'addons.xml'), 'w', encoding='utf-8') as f:
        f.write(addons_xml)

    md5 = hashlib.md5(addons_xml.encode('utf-8')).hexdigest()
    with open(os.path.join(ROOT, 'addons.xml.md5'), 'w') as f:
        f.write(md5)

    print('addons.xml + addons.xml.md5 generati (md5=%s)' % md5)


if __name__ == '__main__':
    main()