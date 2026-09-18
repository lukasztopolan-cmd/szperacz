# Łowca Okazji - OLX + Allegro Lokalnie

### Co to jest?
Aplikacja PWA (działa jak natywna na iPhone/iPad/PC) + backend Python który 24/7 poluje na okazje i wysyła powiadomienia na Telegram w 60 sekund po wystawieniu.

Stworzone dla wielu kategorii na raz - auta, elektronika, rowery, meble.

### Jak uruchomić w 2 minuty (wersja na PC)

1. Zainstaluj Python: https://www.python.org/downloads/
2. W terminalu:
```
pip install requests beautifulsoup4 lxml
python backend.py
```
3. Edytuj `hunters.json` - dodaj swoje wyszukiwania

### Jak podłączyć Telegram (30s)

1. W Telegramie znajdź @BotFather -> /newbot -> nazwij bota
2. Skopiuj TOKEN
3. Wklej w backend.py -> TELEGRAM_TOKEN
4. Napisz cokolwiek do swojego bota
5. Uruchom backend.py - wykryje chat_id automatycznie

### Jak zainstalować jako aplikacja na iPhone

1. Otwórz index.html na hostingu lub lokalnie
2. Kliknij Udostępnij (kwadrat ze strzałką) -> Dodaj do ekranu początkowego
3. Masz ikonę jak normalna apka

### Jak wrzucić na darmowy hosting 24/7

Najprostszy: Render.com
- Załóż konto na render.com
- New -> Background Worker -> podłącz to repo
- Start command: python backend.py
- Dodaj env var TELEGRAM_TOKEN
- Gotowe, działa 24/7 za darmo (750h/mies)

Alternatywy: Fly.io, Railway.app, Hetzner VPS 20zł/mies

### Koszty

- Start: 0 zł
- Domena (opcjonalnie): 50zł/rok
- VPS gdy urośnie: 20-40zł/mies
- Apple Developer (dopiero gdy chcesz App Store): 99$/rok

### Co dalej?

- Chcesz wersję natywną iOS? Ten sam backend, dorabiamy tylko apke w SwiftUI
- Chcesz AI do oceny okazji? Mogę dodać analizę cen vs średnia rynkowa
- Chcesz filtry: rocznik, przebieg, paliwo dla aut? Dodaję w 1h

Autor: Agent Arena.ai
