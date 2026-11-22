#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera il repository Kodi per Burlesco (hosting su GitHub Pages).

In questo repository (burlesco) NON c'e' la sorgente del plugin: c'e' solo la
BUILD (lo zip precompilato) in plugin.video.castellano/<id>-<versione>.zip.
La sorgente del plugin si sviluppa nel progetto separato plugin_kodi.

Questo script:
  - repository.burlesco: e' sorgente (addon.xml + icon.png) -> crea lo zip
  - plugin.video.castellano: e' uno zip pre-buildato -> legge addon.xml dallo
    zip e lo ricopia nella cartella di pubblicazione
  - compone addons.xml (indice) + addons.xml.md5
  - pubblica tutto in public/ (che la CI invia su gh-pages)

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

EXCLUDE_DIRS = {'__pycache__', '.git', '.github', 'public'}
EXCLUDE_FILES = {'.gitignore', 'Thumbs.db', '.DS_Store', 'config.json'}

# Tipi di add-on:
#  'source' -> cartella con addon.xml (lo zippizziamo noi)
#  'binary' -> zip pre-buildato già pronto (lo ricopiamo e basta)
ADDONS = [
    {'id': 'repository.burlesco',     'type': 'source'},
    {'id': 'plugin.video.castellano', 'type': 'binary'},
]


def read_version_source(addon_dir):
    p = os.path.join(ROOT, addon_dir, 'addon.xml')
    with open(p, encoding='utf-8') as f:
        data = f.read()
    m = re.search(r'<addon\b[^>]*\bversion="([^"]+)"', data)
    if not m:
        sys.exit('Versione non trovata in %s/addon.xml' % addon_dir)
    return m.group(1), data


def addon_element_from_xml(data):
    data = re.sub(r'<\?xml[^>]*\?>', '', data).strip()
    m = re.search(r'<addon\b.*?</addon>', data, re.S)
    if not m:
        sys.exit('Elemento <addon> non trovato')
    return m.group(0)


def addon_element_from_zip(zip_path, addon_id):
    with zipfile.ZipFile(zip_path) as z:
        name = '%s/addon.xml' % addon_id
        return addon_element_from_xml(z.read(name).decode('utf-8'))


def make_source_zip(addon_dir, version):
    addon_id = os.path.basename(addon_dir)
    base = os.path.join(ROOT, addon_dir)
    out_dir = os.path.join(OUT, addon_id)
    os.makedirs(out_dir, exist_ok=True)
    out_zip = os.path.join(out_dir, '%s-%s.zip' % (addon_id, version))
    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for name in files:
                if name in EXCLUDE_FILES or name.endswith(('.pyc', '.pyo', '.zip')):
                    continue
                full = os.path.join(root, name)
                rel = os.path.relpath(full, base)
                z.write(full, '%s/%s' % (addon_id, rel.replace('\\', '/')))
    return out_zip


def find_binary_zip(addon_id):
    d = os.path.join(ROOT, addon_id)
    if not os.path.isdir(d):
        sys.exit('Cartella %s non trovata (manca la build)' % addon_id)
    zips = [f for f in os.listdir(d) if f.endswith('.zip')]
    if not zips:
        sys.exit('Nessuno zip in %s/ (esegui build.py nel progetto plugin_kodi '
                 'e copia qui lo zip)' % addon_id)
    # se piu' zip, prendi quello col nome piu' lungo (versione piu' specifica)
    zips.sort(key=len, reverse=True)
    return os.path.join(d, zips[0])


def publish_binary_zip(addon_id, zip_path):
    out_dir = os.path.join(OUT, addon_id)
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, os.path.basename(zip_path))
    shutil.copy(zip_path, dest)
    return dest


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    idx_src = os.path.join(ROOT, 'index.html')
    if os.path.isfile(idx_src):
        shutil.copy(idx_src, os.path.join(OUT, 'index.html'))

    elements = []
    for spec in ADDONS:
        addon_id = spec['id']
        if spec['type'] == 'source':
            version, data = read_version_source(addon_id)
            addon_el = addon_element_from_xml(data)
            zpath = make_source_zip(addon_id, version)
        else:  # binary
            zpath = find_binary_zip(addon_id)
            addon_el = addon_element_from_zip(zpath, addon_id)
            publish_binary_zip(addon_id, zpath)
            m = re.search(r'version="([^"]+)"', addon_el)
            version = m.group(1) if m else '?'
        elements.append(addon_el)
        print('  %-28s v%s  (zip pronto)' % (addon_id, version))

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