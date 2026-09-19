# 🚀 Łowca Okazji - Deploy na Render.com 1-KLIK (darmowe 24/7)

## Opcja 1: Najprostsza - Deploy bez GitHub (3 minuty)

1. Wejdź na **https://dashboard.render.com/**
2. Kliknij **New +** -> **Background Worker**
3. Wybierz **Deploy from public Git repo** lub **Upload** (jeśli masz ZIP)
   
   **Jeśli masz GitHub:**
   - Wrzuć folder `olx-hunter-FINAL` na GitHub jako nowe repo
   - W Render wybierz to repo
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python backend.py`
   - Kliknij **Advanced** -> **Add Environment Variable**
     - Key: `TELEGRAM_TOKEN`
     - Value: Twój NOWY token od @BotFather (po revoke!)
   - Create Worker

   **Jeśli NIE masz GitHub (prostsze):**
   - Wejdź na https://render.com/docs/deploy-from-github ale wybierz "Public Git repository"
   - Użyj tego repo jako template: https://github.com/render-examples/python-telegram-bot lub po prostu wrzuć pliki ręcznie

4. Po deploy, w logach Render zobaczysz:
```
🤖 Sprawdzam Telegram...
❌ Nie znaleziono wiadomości. Napisz najpierw cokolwiek do swojego bota!
```

5. Otwórz Telegram, napisz cokolwiek do swojego bota (np. "hej")
6. W logach Render pojawi się:
```
✅ Wykryto Telegram chat_id: 123456789
🧪 Test Telegram...
✅ Wysłano: TEST - BMW E90...
```
7. Dostajesz testową wiadomość na Telegram = **DZIAŁA 24/7!**

## Opcja 2: 1-KLIK Deploy Button (jeśli wrzucisz na GitHub)

Dodaj do README.md swojego repo:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/TWOJ_USERNAME/lowca-okazji)

Po kliknięciu Render sam poprosi o `TELEGRAM_TOKEN` i zdeployuje.

## Pliki w paczce:

- `backend.py` - główny bot, szuka co 90s na OLX i Allegro Lokalnie
- `requirements.txt` - biblioteki Python
- `render.yaml` - konfiguracja dla Render (auto-deploy)
- `hunters.json` - Twoi łowcy (marka, model, rocznik, paliwo, prywatny/firma, lokalizacja od Ciebie)
- `index.html` - frontend PWA (hostuj na Netlify Drop)

## Jak dodać łowców?

Edytuj `hunters.json` na Render.com (Shell) lub lokalnie i push na GitHub:

```json
{
  "name": "BMW E90 diesel prywatny do 15k 30km ode mnie",
  "portal": "both",
  "keyword": "bmw e90",
  "price_to": 15000,
  "brand": "BMW",
  "fuel": "diesel",
  "seller_type": "private",
  "radius": 30,
  "active": true
}
```

Nowe filtry:
- `brand`: BMW, Audi, VW, Mercedes, Opel, Ford, Toyota, Skoda, Renault...
- `seller_type`: "private" (osoba prywatna) lub "business" (firma)
- `fuel`: petrol, diesel, lpg, hybrid, electric
- `gearbox`: manual, automatic
- `damaged`: "yes" (uszkodzone okazje) lub "no" (nieuszkodzone)

## Darmowe limity Render.com:

- 750 godzin / miesiąc za darmo (wystarcza na 24/7)
- Background Worker śpi po 15 min bez aktywności? Nie, worker działa cały czas
- Jeśli chcesz 100% uptime, dodaj kartę (nie pobiera pieniędzy na free tier) lub użyj cron job co 10 min

## Problemy?

- `401 Unauthorized` -> zły token, zrób revoke w @BotFather i wklej nowy
- `Brak chat_id` -> napisz coś do bota na Telegramie
- Bot nie wysyła -> sprawdź logi w Render Dashboard -> Logs

Gotowe! Bot działa 24/7 i wysyła Ci okazje z dźwiękiem na Telegram.
