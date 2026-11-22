# Burlesco — Repository Kodi

Repository sorgente Kodi per installare e aggiornare automaticamente gli add-on
di Burlesco (es. **Castellano - TV spagnola**).

URL da aggiungere in Kodi:

```
https://Burlesco70.github.io/burlesco
```

> Questo repository **non contiene la sorgente del plugin**: contiene solo la
> build (lo zip precompilato) in `plugin.video.castellano/`. Lo sviluppo del
> plugin avviene nel progetto separato `plugin_kodi`.

## Come si usa in Kodi

1. **Aggiungi sorgente**: Sistema → Impostazioni → Add-on → Origini → Aggiungi
   sorgente file → incolla `https://Burlesco70.github.io/burlesco` → nome
   "Burlesco" → OK.
2. **Installa il repository**: Add-on → Installa da file ZIP → sorgente Burlesco
   → `repository.burlesco-1.0.0.zip`.
   - In alternativa scarica e installa direttamente lo zip del repository.
3. **Installa gli add-on**: Add-on → Installa da repository → Burlesco →
   Castellano → Installa.

Da qui Kodi controllerà da solo gli aggiornamenti.

## Struttura

```
burlesco/
├── addons.xml                (indice del repository — generato)
├── addons.xml.md5            (checksum — generato)
├── generate.py               (genera addons.xml + zip in public/)
├── release.py                (build plugin + copia zip + commit/push)
├── index.html                (pagina di benvenuto / link per install)
├── repository.burlesco/      (add-on repository: addon.xml + icon.png)
│   ├── addon.xml
│   ├── icon.png
│   └── repository.burlesco-1.0.0.zip   (generato)
├── plugin.video.castellano/
│   └── plugin.video.castellano-<versione>.zip   (BUILD precompilata)
└── .github/workflows/publish.yml
```

## Pubblicazione / aggiornamenti

Un workflow GitHub Actions (`publish.yml`) esegue `generate.py` e pubblica il
risultato (cartella `public/`) sul branch `gh-pages` a ogni push su `main`.

Configurazione iniziale (una volta sola):
- **Settings → Pages → Build and deployment → Source: Deploy from a branch**
- **Branch: `gh-pages` / (root)** → Save.

### Rilascio di una nuova versione del plugin

Hai due modi:

**A) Tutto in un colpo con `release.py`** (consigliato)

Assumendo i due progetti affiancati (`plugin_kodi` e `burlesco` nella stessa
cartella):

```
cd burlesco
python release.py "messaggio del commit opzionale"
```

Lo script:
1. esegue `build.py` nel progetto `plugin_kodi`;
2. copia lo zip risultante in `burlesco/plugin.video.castellano/`;
3. fa `git add`, `git commit` e `git push` su `burlesco`.

(Se i progetti non sono affiancati, passa il percorso:
`python release.py --plugin-dir "C:\path\plugin_kodi"`.)

**B) Manuale**

1. In `plugin_kodi`: aggiorna `version="..."` (e `<news>`) in `addon.xml`, poi
   `python build.py`.
2. Copia `plugin_kodi/plugin/plugin.video.castellano-<versione>.zip` in
   `burlesco/plugin.video.castellano/`.
3. In `burlesco`: `git add . && git commit -m "release <versione>" && git push`.

In entrambi i casi la CI rigenera e pubblica: dopo poco l'aggiornamento è
disponibile in Kodi.

## Test in locale

```
python generate.py
```

Genera `public/` con `addons.xml`, `addons.xml.md5` e gli zip.