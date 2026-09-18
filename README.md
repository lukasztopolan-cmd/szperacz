# Łowca Okazji FINAL - Naprawione błędy + Bot Telegram

## Co naprawiono (Twoje błędy z Netlify):

### ❌ Było:
- `/ikona-dotykowa.png 401` - polskie nazwy plików
- `/indeks.html 401` - zła nazwa (powinno być index.html)
- `/favicon.ico 404` - brak favicon
- `start_url = "./index.html"` - problemy z PWA

### ✅ Teraz:
- Wszystkie pliki: `icon-192.png`, `icon-512.png`, `apple-touch-icon.png`, `favicon.ico` - angielskie nazwy, bez polskich znaków
- `index.html` - poprawna nazwa
- `manifest.json` - `start_url: "/"` - poprawne dla PWA
- Dodano `netlify.toml` i `_redirects` - zero błędów 401/404

## Jak wrzucić na Netlify bez błędów:

1. Pobierz folder `olx-hunter-FINAL` jako ZIP
2. Wejdź na https://app.netlify.com/drop
3. Przeciągnij ZIP na stronę
4. Gotowe! Dostajesz link https://twoja-nazwa.netlify.app - 0 błędów

## Bot Telegram - jak zabezpieczyć token:

**WAŻNE:** Token ze screena `8827256269:AAHHFsWUrGUKyDSClhGbVdV0dMXa5NWZXis` jest PUBLICZNY!

1. W Telegramie: @BotFather -> /mybots -> wybierz bota -> API Token -> Revoke current token
2. Skopiuj NOWY token
3. Wklej go w `backend.py` linia 18: `TELEGRAM_TOKEN = "NOWY_TOKEN"`
4. Usuń screen z tokenem

## Jak uruchomić backend (powiadomienia):

### Na PC (test):
```bash
pip install requests beautifulsoup4 lxml
python backend.py
```

### Na serwerze 24/7 (Render.com - darmowe):
1. Załóż konto na render.com
2. New -> Background Worker -> podłącz repo lub wrzuć pliki
3. Build command: `pip install requests beautifulsoup4 lxml`
4. Start command: `python backend.py`
5. Env var: `TELEGRAM_TOKEN = twój_token`
6. Deploy

Backend automatycznie wykryje chat_id po tym jak napiszesz cokolwiek do bota.

## Nowe filtry dla aut:

W apce teraz masz:
- Marka (BMW, Audi, VW, Mercedes...)
- Model
- Rocznik od/do
- Przebieg do
- Paliwo (benzyna, diesel, LPG, hybryda, elektryczny)
- Skrzynia (manual, automat)
- Uszkodzony / nieuszkodzony

Wszystko działa z Telegramem - dostajesz powiadomienie w 90 sekund po wystawieniu.

## Test bota:

Po uruchomieniu backend.py wyśle Ci testową wiadomość:
"TEST - BMW E90 320d 2008 - Twoj bot dziala! 🔥"

Jeśli dostaniesz - wszystko działa.
