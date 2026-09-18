"""
ŁOWCA OKAZJI - Backend Python
Działa na PC, VPS, Render.com, Fly.io - 24/7
Sprawdza OLX i Allegro Lokalnie + wysyła na Telegram

Instalacja:
pip install requests beautifulsoup4 lxml

Uruchomienie:
python backend.py

Co musisz ustawić:
1. TELEGRAM_TOKEN - od @BotFather
2. Hunters w hunters.json (albo przez API)
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import os
import re
from datetime import datetime

# ========== KONFIGURACJA ==========
TELEGRAM_TOKEN = "WKLEJ_TUTAJ_TOKEN_OD_BOTFATHER"  # np. 123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
TELEGRAM_CHAT_ID = None  # zostanie wykryte automatycznie po pierwszej wiadomości do bota

CHECK_INTERVAL = 120  # co ile sekund sprawdzać (120 = 2 minuty)
DATA_FILE = "seen_offers.json"
HUNTERS_FILE = "hunters.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Accept-Language": "pl-PL,pl;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

# Przykładowe łowcy - możesz edytować plik hunters.json
DEFAULT_HUNTERS = [
    {
        "name": "BMW do 15k Wrocław",
        "portal": "both",  # olx, allegro, both
        "keyword": "bmw e90",
        "price_to": 15000,
        "price_from": 5000,
        "location": "wroclaw",
        "radius": 100,
        "active": True
    },
    {
        "name": "iPhone 13 do 1800",
        "portal": "olx",
        "keyword": "iphone 13",
        "price_to": 1800,
        "location": "wroclaw",
        "active": True
    }
]

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_telegram_chat_id():
    """Automatycznie znajduje chat_id po tym jak napiszesz do bota"""
    global TELEGRAM_CHAT_ID
    if TELEGRAM_CHAT_ID:
        return TELEGRAM_CHAT_ID
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        r = requests.get(url, timeout=10).json()
        if r.get("result"):
            last = r["result"][-1]
            chat_id = last["message"]["chat"]["id"]
            print(f"✅ Wykryto Telegram chat_id: {chat_id}")
            TELEGRAM_CHAT_ID = chat_id
            return chat_id
    except Exception as e:
        print(f"⚠️ Nie udało się pobrać chat_id: {e}")
    return None

def send_telegram(offer, hunter_name):
    """Wysyła powiadomienie na Telegram"""
    if TELEGRAM_TOKEN.startswith("WKLEJ"):
        print(f"🔕 [MOCK TELEGRAM] {hunter_name}: {offer['title']} - {offer['price']} - {offer['url']}")
        return
    
    chat_id = get_telegram_chat_id()
    if not chat_id:
        print("❌ Najpierw napisz cokolwiek do swojego bota na Telegramie!")
        return

    text = f"""🔥 <b>NOWA OKAZJA! {hunter_name}</b>

<b>{offer['title']}</b>
💰 <b>{offer['price']}</b>
📍 {offer['location']}
🏷️ {offer['portal']}

🔗 <a href="{offer['url']}">OTWÓRZ OGŁOSZENIE</a>

⏰ {datetime.now().strftime('%H:%M:%S')}
"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
        # Jeśli jest zdjęcie, wyślij jako foto
        if offer.get('image'):
            url_photo = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            payload_photo = {
                "chat_id": chat_id,
                "caption": text,
                "parse_mode": "HTML",
                "photo": offer['image']
            }
            requests.post(url_photo, data=payload_photo, timeout=10)
        else:
            requests.post(url, data=payload, timeout=10)
        print(f"✅ Wysłano na Telegram: {offer['title']}")
    except Exception as e:
        print(f"❌ Błąd Telegram: {e}")

def search_olx(hunter):
    """Scraper OLX - wersja odporna na Cloudflare"""
    offers = []
    try:
        keyword = hunter['keyword'].replace(' ', '-')
        # Budujemy URL OLX
        url = f"https://www.olx.pl/d/oferty/q-{keyword}/"
        params = []
        if hunter.get('price_from'):
            params.append(f"search%5Bfilter_float_price:from%5D={hunter['price_from']}")
        if hunter.get('price_to'):
            params.append(f"search%5Bfilter_float_price:to%5D={hunter['price_to']}")
        if hunter.get('location'):
            # OLX location - uproszczone, można rozbudować
            pass
        if params:
            url += "?" + "&".join(params)

        print(f"🔍 OLX: {url}")
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'lxml')

        # OLX ma różne selektory, próbujemy kilku
        cards = soup.select('[data-cy="l-card"]') or soup.select('.css-1sw7q4x') or soup.select('div[data-testid="l-card"]')
        
        for card in cards[:10]:  # max 10 najnowszych
            try:
                title_el = card.select_one('h6') or card.select_one('[data-cy="ad-card-title"]') or card.select_one('a > h6')
                price_el = card.select_one('[data-testid="ad-price"]') or card.select_one('p[data-testid="ad-price"]')
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

                # ID oferty z URL
                offer_id = re.search(r'-ID([a-zA-Z0-9]+)\.html', href)
                offer_id = offer_id.group(1) if offer_id else href

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
    """Scraper Allegro Lokalnie"""
    offers = []
    try:
        keyword = hunter['keyword'].replace(' ', '%20')
        url = f"https://allegrolokalnie.pl/oferty/q/{keyword}"
        # Filtry ceny Allegro Lokalnie
        # ?price_from=...&price_to=...
        params = []
        if hunter.get('price_from'):
            params.append(f"price_from={hunter['price_from']}")
        if hunter.get('price_to'):
            params.append(f"price_to={hunter['price_to']}")
        if params:
            url += "?" + "&".join(params)

        print(f"🔍 Allegro Lokalnie: {url}")
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'lxml')

        cards = soup.select('[data-testid="listing-item"]') or soup.select('article') or soup.select('div.ml-offer')

        for card in cards[:10]:
            try:
                title_el = card.select_one('h2') or card.select_one('a')
                price_el = card.select_one('[data-testid="price"]') or card.select_one('span')
                link_el = card.select_one('a')

                if not title_el or not link_el:
                    continue

                title = title_el.get_text(strip=True)[:100]
                href = link_el.get('href')
                if href and not href.startswith('http'):
                    href = "https://allegrolokalnie.pl" + href
                
                # cena
                price_text = ""
                if price_el:
                    price_text = price_el.get_text(strip=True)
                # spróbuj wyciągnąć cenę regexem
                if not price_text or "zł" not in price_text:
                    m = re.search(r'\d[\d\s]*zł', card.get_text())
                    price_text = m.group(0) if m else "Sprawdź cenę"

                offers.append({
                    "id": f"allegro_{href.split('/')[-1][:30]}",
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

def main():
    print("🚀 ŁOWCA OKAZJI STARTUJE")
    print(f"⏱ Sprawdzam co {CHECK_INTERVAL}s")
    print("="*50)

    # Przygotuj pliki
    if not os.path.exists(HUNTERS_FILE):
        save_json(HUNTERS_FILE, DEFAULT_HUNTERS)
        print(f"📄 Utworzono {HUNTERS_FILE} - edytuj go żeby dodać swoje wyszukiwania!")

    seen = load_json(DATA_FILE, {})
    
    while True:
        hunters = load_json(HUNTERS_FILE, DEFAULT_HUNTERS)
        active_hunters = [h for h in hunters if h.get('active', True)]
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Sprawdzam {len(active_hunters)} łowców...")

        for hunter in active_hunters:
            print(f"\n-- {hunter['name']} ({hunter['keyword']}) --")
            all_offers = []

            if hunter['portal'] in ['olx', 'both']:
                all_offers.extend(search_olx(hunter))
                time.sleep(2)  # anty-ban

            if hunter['portal'] in ['allegro', 'both']:
                all_offers.extend(search_allegro_lokalnie(hunter))
                time.sleep(2)

            # Sprawdź nowe
            new_count = 0
            for offer in all_offers:
                if offer['id'] not in seen:
                    seen[offer['id']] = datetime.now().isoformat()
                    send_telegram(offer, hunter['name'])
                    new_count += 1
            
            print(f"✅ {hunter['name']}: {len(all_offers)} znalezionych, {new_count} nowych")
            save_json(DATA_FILE, seen)

        print(f"\n💤 Śpię {CHECK_INTERVAL}s...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
