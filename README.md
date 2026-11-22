# Burlesco — Repository Kodi

Repository sorgente Kodi per installare e aggiornare automaticamente gli add-on
di Burlesco (es. **Castellano - TV spagnola**).

URL da aggiungere in Kodi:

```
https://Burlesco70.github.io/burlesco
```

## Come si usa in Kodi

1. **Aggiungi sorgente**: Sistema → Impostazioni → Add-on → Origini → Aggiungi
   sorgente file → incolla `https://Burlesco70.github.io/burlesco` → dai un nome
   (es. "Burlesco") → OK.
2. **Installa il repository**: Add-on → Installa da file ZIP (o "Cerca")
   → repository.burlesco → installa.
   - In alternativa installa direttamente lo zip:
     `https://Burlesco70.github.io/burlesco/repository.burlesco/repository.burlesco-1.0.0.zip`
3. **Installa gli add-on**: Add-on → Cerca → Burlesco → Castellano → Installa.

Da qui Kodi controllerà da solo gli aggiornamenti.

## Struttura

```
burlesco/
├── addons.xml                (indice del repository — generato)
├── addons.xml.md5            (checksum — generato)
├── generate.py               (genera addons.xml + zip)
├── repository.burlesco/      (add-on repository)
│   ├── addon.xml
│   ├── icon.png
│   └── repository.burlesco-1.0.0.zip   (generato)
├── plugin.video.castellano/  (add-on TV spagnola)
│   ├── addon.xml
│   └── plugin.video.castellano-1.0.0.zip  (generato)
└── .github/workflows/publish.yml
```

## Pubblicazione / aggiornamenti

Un workflow GitHub Actions rigenera `addons.xml` e gli zip e li pubblica sul
branch `gh-pages` a ogni push su `main`.

Serve configurare una sola volta:
- **Settings → Pages → Build and deployment → Source: Deploy from a branch**
- **Branch: `gh-pages` / (root)** → Save.

Per rilasciare una nuova versione di un add-on:
1. aggiorna `version="..."` (e `<news>`) nell'`addon.xml` dell'add-on;
2. fai commit e push su `main`;
3. la CI rigenera e pubblica: dopo poco l'aggiornamento è disponibile in Kodi.

## Test in locale

```
python generate.py
```

Genera `addons.xml`, `addons.xml.md5` e gli zip nella root.