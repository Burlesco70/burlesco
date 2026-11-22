#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Release di plugin.video.castellano in un colpo solo.

Passi:
  1. esegue build.py nel progetto plugin_kodi (genera lo zip)
  2. copia lo zip in burlesco/plugin.video.castellano/
  3. git add + commit + push nel repo burlesco (-> parte la CI su GitHub Pages)

Uso (dalla cartella burlesco):
    python release.py ["messaggio commit"]
    python release.py --plugin-dir "C:\\path\\plugin_kodi" ["messaggio"]
    python release.py --no-push        # solo build+copia+commit, niente push

Requisiti: i progetti plugin_kodi e burlesco affiancati (default), oppure
specifica --plugin-dir.
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ADDON_ID = 'plugin.video.castellano'


def run(cmd, cwd=None, check=True):
    print('$', ' '.join(cmd), ('  (in %s)' % cwd if cwd else ''))
    res = subprocess.run(cmd, cwd=cwd)
    if check and res.returncode != 0:
        sys.exit('Comando fallito (%d): %s' % (res.returncode, ' '.join(cmd)))


def find_plugin_dir(arg):
    if arg:
        return os.path.abspath(arg)
    # default: plugin_kodi affiancato a burlesco
    sibling = os.path.join(os.path.dirname(HERE), 'plugin_kodi')
    if os.path.isdir(sibling):
        return sibling
    sys.exit('plugin_kodi non trovato accanto a burlesco. '
             'Usa --plugin-dir "percorso\\plugin_kodi".')


def python_exe():
    return sys.executable or 'python'


def main():
    ap = argparse.ArgumentParser(description='Build + copia + commit/push release')
    ap.add_argument('message', nargs='?', default=None,
                    help='messaggio del commit')
    ap.add_argument('--plugin-dir', default=None,
                    help='percorso del progetto plugin_kodi')
    ap.add_argument('--no-push', action='store_true',
                    help='non eseguire git push')
    args = ap.parse_args()

    plugin_dir = find_plugin_dir(args.plugin_dir)
    print('Progetto plugin :', plugin_dir)
    print('Repo burlesco   :', HERE)

    # 1) build nel progetto plugin
    run([python_exe(), 'build.py'], cwd=plugin_dir)

    # individua lo zip appena creato
    pattern = os.path.join(plugin_dir, 'plugin', '%s-*.zip' % ADDON_ID)
    zips = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    if not zips:
        sys.exit('Nessuno zip trovato: %s' % pattern)
    zip_path = zips[0]
    print('Zip buildato   :', zip_path)

    # 2) copia in burlesco/<id>/
    dest_dir = os.path.join(HERE, ADDON_ID)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, os.path.basename(zip_path))
    shutil.copy(zip_path, dest)
    print('Copiato in     :', dest)

    # 3) git add/commit/push
    run(['git', 'add', '-A'], cwd=HERE)
    msg = args.message or 'Release %s (%s)' % (
        ADDON_ID, os.path.basename(zip_path))
    # commit (ignora se non cambia nulla)
    res = subprocess.run(['git', 'commit', '-m', msg], cwd=HERE)
    if res.returncode != 0:
        print('Niente da committare o commit fallito; proseguo.')
    if not args.no_push:
        run(['git', 'push'], cwd=HERE)
        print('\nPush completato. La CI pubblicherà su GitHub Pages.')
        print('Verifica: https://Burlesco70.github.io/burlesco/addons.xml')
    else:
        print('\n--no-push: build+copia+commit eseguiti, senza push.')


if __name__ == '__main__':
    main()