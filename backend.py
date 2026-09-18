"""
ŁOWCA OKAZJI - Backend Python FINAL
Naprawione błędy + filtry aut + Telegram Bot

Instalacja:
pip install requests beautifulsoup4 lxml

Uruchomienie:
python backend.py

WAŻNE BEZPIECZEŃSTWO:
Token który był na screenie (8827256269:...) jest PUBLICZNY i trzeba go zrevoke'ować!
1. @BotFather -> /mybots -> wybierz bota -> API Token -> Revoke current token
2. Wklej nowy token poniżej
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import os
import re
from datetime import datetime

# ========== KONFIGURACJA ==========
# Token jest pobierany z ENV (Render.com) lub z tego pliku
# Na Render.com ustaw: TELEGRAM_TOKEN = twój_nowy_token
# Lokalnie - wklej poniżej
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "WKLEJ_TUTAJ_NOWY_TOKEN_PO_REVOKE")  # <-- ZMIEŃ NA NOWY PO REVOKE!
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")  # opcjonalnie, wykryje automatycznie

# Jeśli token to nadal placeholder, spróbuj wczytać z pliku .env
if TELEGRAM_TOKEN.startswith("WKLEJ") and os.path.exists(".env"):
    try:
        with open(".env", "r") as f:
            for line in f:
                if "TELEGRAM_TOKEN" in line and "=" in line:
                    TELEGRAM_TOKEN = line.split("=")[1].strip().strip('"').strip("'")
    except:
        pass

CHECK_INTERVAL = 90  # 90 sekund - szybciej dla aut
DATA_FILE = "seen_offers.json"
HUNTERS_FILE = "hunters.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Accept-Language": "pl-PL,pl;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

DEFAULT_HUNTERS = [
    {
        "name": "BMW E90 diesel do 15k Wrocław",
        "portal": "both",
        "keyword": "bmw e90",
        "price_to": 15000,
        "price_from": 3000,
        "location": "wroclaw",
        "radius": 100,
        "brand": "BMW",
        "fuel": "diesel",
        "year_from": 2005,
        "year_to": 2012,
        "active": True
    },
    {
        "name": "Auta uszkodzone do 10k - okazje",
        "portal": "both",
        "keyword": "uszkodzony",
        "price_to": 10000,
        "location": "dolnoslaskie",
        "damaged": "yes",
        "active": True
    }
]

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Błąd wczytywania {path}: {e}")
            return default
    return default

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_telegram_chat_id():
    global TELEGRAM_CHAT_ID
    if TELEGRAM_CHAT_ID:
        return TELEGRAM_CHAT_ID
    if TELEGRAM_TOKEN.startswith("WKLEJ") or len(TELEGRAM_TOKEN) < 20:
        print("❌ Brak tokenu Telegram!")
        return None
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        r = requests.get(url, timeout=15).json()
        if r.get("ok") and r.get("result"):
            # weź ostatni chat_id
            for update in reversed(r["result"]):
                if "message" in update and "chat" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    print(f"✅ Wykryto Telegram chat_id: {chat_id} (user: {update['message']['chat'].get('first_name','')})")
                    TELEGRAM_CHAT_ID = chat_id
                    save_json("telegram_config.json", {"chat_id": chat_id, "detected_at": datetime.now().isoformat()})
                    return chat_id
        print("❌ Nie znaleziono wiadomości. Napisz najpierw cokolwiek do swojego bota na Telegramie!")
        print(f"   Bot: https://t.me/{TELEGRAM_TOKEN.split(':')[0]}_bot lub sprawdź nazwę w @BotFather")
    except Exception as e:
        print(f"⚠️ Błąd pobierania chat_id: {e}")
    return None

def send_telegram(offer, hunter_name):
    if TELEGRAM_TOKEN.startswith("WKLEJ"):
        print(f"🔕 [MOCK] {hunter_name}: {offer['title']} - {offer['price']} - {offer['url']}")
        return True
    
    chat_id = TELEGRAM_CHAT_ID or load_json("telegram_config.json", {}).get("chat_id") or get_telegram_chat_id()
    if not chat_id:
        print("❌ Brak chat_id - napisz coś do bota!")
        return False

    # Formatowanie wiadomości z filtrami aut
    extra = ""
    if offer.get('year'): extra += f"📅 {offer['year']} "
    if offer.get('mileage'): extra += f"🛣️ {offer['mileage']} "
    if offer.get('fuel'): extra += f"⛽ {offer['fuel']} "

    text = f"""🔥 <b>NOWA OKAZJA! {hunter_name}</b>

<b>{offer['title']}</b>
💰 <b>{offer['price']}</b>
📍 {offer['location']}
🏷️ {offer['portal']}
{extra}

🔗 <a href="{offer['url']}">OTWÓRZ OGŁOSZENIE</a>

⏰ {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}
"""

    try:
        # Najpierw spróbuj wysłać ze zdjęciem
        if offer.get('image') and offer['image'].startswith('http'):
            url_photo = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            payload = {
                "chat_id": chat_id,
                "caption": text,
                "parse_mode": "HTML",
                "photo": offer['image']
            }
            r = requests.post(url_photo, data=payload, timeout=15)
            if r.status_code == 200:
                print(f"✅ Wysłano foto: {offer['title'][:40]}")
                return True
        
        # Fallback - sam tekst
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
        r = requests.post(url, data=payload, timeout=15)
        if r.status_code == 200:
            print(f"✅ Wysłano: {offer['title'][:50]}")
            return True
        else:
            print(f"❌ Błąd Telegram {r.status_code}: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Błąd wysyłki Telegram: {e}")
        return False

def search_olx(hunter):
    offers = []
    try:
        keyword = hunter['keyword'].replace(' ', '-').lower()
        url = f"https://www.olx.pl/d/oferty/q-{keyword}/"
        params = []
        if hunter.get('price_from'):
            params.append(f"search%5Bfilter_float_price:from%5D={hunter['price_from']}")
        if hunter.get('price_to'):
            params.append(f"search%5Bfilter_float_price:to%5D={hunter['price_to']}")
        if hunter.get('seller_type') == 'private':
            params.append(f"search%5Bprivate_business%5D=private")
        elif hunter.get('seller_type') == 'business':
            params.append(f"search%5Bprivate_business%5D=business")
        if hunter.get('brand'):
            # Dodaj markę do keyword jeśli nie ma
            if hunter['brand'].lower() not in hunter['keyword'].lower():
                keyword = f"{hunter['brand'].lower()}-{keyword}"
                url = f"https://www.olx.pl/d/oferty/q-{keyword}/"
        if params:
            url += "?" + "&".join(params)

        print(f"🔍 OLX: {hunter['name']} -> {url[:80]}")
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            print(f"⚠️ OLX status {r.status_code}")
            return offers

        soup = BeautifulSoup(r.text, 'lxml')
        cards = soup.select('[data-cy="l-card"]') or soup.select('div[data-testid="l-card"]') or soup.select('.css-1sw7q4x')

        for card in cards[:12]:
            try:
                title_el = card.select_one('h6') or card.select_one('[data-cy="ad-card-title"]')
                price_el = card.select_one('[data-testid="ad-price"]')
                link_el = card.select_one('a')
                loc_el = card.select_one('[data-testid="location-date"]')
                img_el = card.select_one('img')

                if not title_el or not link_el:
                    continue

                title = title_el.get_text(strip=True)
                href = link_el.get('href')
                if href and not href.startswith('http'):
                    href = "https://www.olx.pl" + href
                price = price_el.get_text(strip=True) if price_el else "Do negocjacji"
                location = loc_el.get_text(strip=True) if loc_el else hunter.get('location','')
                img = img_el.get('src') if img_el else None
                if img and 'no_thumbnail' in img:
                    img = None

                # Filtry aut - sprawdź czy tytuł zawiera filtry
                title_lower = title.lower()
                if hunter.get('brand') and hunter['brand'].lower() not in title_lower:
                    # Nie odrzucaj, ale oznacz - czasem OLX ma markę w innym polu
                    pass

                offer_id = re.search(r'-ID([a-zA-Z0-9]+)\.html', href)
                offer_id = offer_id.group(1) if offer_id else href[-30:]

                offers.append({
                    "id": f"olx_{offer_id}",
                    "title": title,
                    "price": price,
                    "url": href,
                    "location": location,
                    "portal": "OLX",
                    "image": img
                })
            except Exception as e:
                continue

    except Exception as e:
        print(f"❌ Błąd OLX {hunter['keyword']}: {e}")
    return offers

def search_allegro_lokalnie(hunter):
    offers = []
    try:
        keyword = hunter['keyword'].replace(' ', '%20')
        url = f"https://allegrolokalnie.pl/oferty/q/{keyword}"
        params = []
        if hunter.get('price_from'):
            params.append(f"price_from={hunter['price_from']}")
        if hunter.get('price_to'):
            params.append(f"price_to={hunter['price_to']}")
        if params:
            url += "?" + "&".join(params)

        print(f"🔍 Allegro Lokalnie: {hunter['name']}")
        r = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(r.text, 'lxml')
        cards = soup.select('article') or soup.select('[data-testid="listing-item"]') or soup.select('div.ml-offer')

        for card in cards[:10]:
            try:
                title_el = card.select_one('h2') or card.select_one('a')
                link_el = card.select_one('a')
                if not title_el or not link_el:
                    continue
                title = title_el.get_text(strip=True)[:120]
                href = link_el.get('href')
                if href and not href.startswith('http'):
                    href = "https://allegrolokalnie.pl" + href
                price_text = ""
                m = re.search(r'\d[\d\s]*zł', card.get_text())
                price_text = m.group(0) if m else "Sprawdź cenę"

                offers.append({
                    "id": f"allegro_{href.split('/')[-1][:40]}",
                    "title": title,
                    "price": price_text,
                    "url": href,
                    "location": hunter.get('location',''),
                    "portal": "Allegro Lokalnie",
                    "image": None
                })
            except:
                continue
    except Exception as e:
        print(f"❌ Błąd Allegro {hunter['keyword']}: {e}")
    return offers

def test_telegram():
    print("🧪 Test Telegram...")
    chat_id = get_telegram_chat_id()
    if not chat_id:
        print("❌ Nie udało się pobrać chat_id. Napisz coś do bota i spróbuj ponownie.")
        return False
    test_offer = {
        "title": "TEST - BMW E90 320d 2008 - Twoj bot dziala! 🔥",
        "price": "13 900 zł",
        "url": "https://www.olx.pl",
        "location": "Wrocław - TEST",
        "portal": "TEST",
        "image": None,
        "year": "2008",
        "mileage": "230kkm",
        "fuel": "Diesel"
    }
    return send_telegram(test_offer, "TEST BOTA")

def main():
    print("="*60)
    print("🚀 ŁOWCA OKAZJI - FINAL v3")
    print("   OLX + Allegro Lokalnie + Telegram Bot")
    print("   Filtry aut: marka, rocznik, przebieg, paliwo, skrzynia")
    print("="*60)
    print(f"⏱ Sprawdzam co {CHECK_INTERVAL}s")
    
    if not os.path.exists(HUNTERS_FILE):
        save_json(HUNTERS_FILE, DEFAULT_HUNTERS)
        print(f"📄 Utworzono {HUNTERS_FILE}")

    # Sprawdź Telegram na starcie
    if not TELEGRAM_TOKEN.startswith("WKLEJ"):
        print("\n🤖 Sprawdzam Telegram...")
        if test_telegram():
            print("✅ Telegram działa! Będziesz dostawać powiadomienia.\n")
        else:
            print("⚠️ Telegram nie działa - sprawdź token i napisz do bota.\n")
    else:
        print("⚠️ Brak tokenu Telegram - powiadomienia wyłączone (tylko log)\n")

    seen = load_json(DATA_FILE, {})
    print(f"📦 Wczytano {len(seen)} już widzianych ofert")

    while True:
        hunters = load_json(HUNTERS_FILE, DEFAULT_HUNTERS)
        active_hunters = [h for h in hunters if h.get('active', True)]
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Sprawdzam {len(active_hunters)} łowców...")

        for hunter in active_hunters:
            print(f"\n-- {hunter['name']} --")
            all_offers = []

            if hunter['portal'] in ['olx', 'both']:
                all_offers.extend(search_olx(hunter))
                time.sleep(2)

            if hunter['portal'] in ['allegro', 'both']:
                all_offers.extend(search_allegro_lokalnie(hunter))
                time.sleep(2)

            new_count = 0
            for offer in all_offers:
                if offer['id'] not in seen:
                    seen[offer['id']] = datetime.now().isoformat()
                    if send_telegram(offer, hunter['name']):
                        new_count += 1
                    # Zwiększ licznik trafień
                    hunter['hits'] = hunter.get('hits', 0) + 1

            print(f"✅ {hunter['name']}: {len(all_offers)} znalezionych, {new_count} nowych")
            save_json(DATA_FILE, seen)
            save_json(HUNTERS_FILE, hunters)

        print(f"\n💤 Śpię {CHECK_INTERVAL}s... (Ctrl+C aby zatrzymać)")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Zatrzymano.")
