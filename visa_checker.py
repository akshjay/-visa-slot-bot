import os
import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

URLS = {
    "Chennai": "https://checkvisaslots.com/visa-slots-info/in/b1-b2-regular/",
    "Hyderabad": "https://checkvisaslots.com/visa-slots-info/in/b1-b2-regular/",
}

KEYWORDS_AVAILABLE = ["chennai", "hyderabad", "available", "slots found"]
KEYWORDS_UNAVAILABLE = ["no slots", "no appointments", "not available", "unavailable"]

def send_telegram(message):
    import requests
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)

def check_slots():
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = browser.new_context()
        page = context.new_page()

        for city, url in URLS.items():
            try:
                print(f"Checking {city}...")
                page.goto(url, timeout=30000)
                page.wait_for_load_state("networkidle", timeout=15000)

                content = page.content().lower()

                unavailable = any(kw in content for kw in KEYWORDS_UNAVAILABLE)
                available = any(kw in content for kw in KEYWORDS_AVAILABLE)

                if unavailable:
                    results[city] = False
                elif available:
                    results[city] = True
                else:
                    results[city] = None  # page loaded but unclear

                print(f"{city}: {'✅ SLOT FOUND' if results[city] else '❌ No slot'}")

            except PlaywrightTimeout:
                print(f"⚠️ Timeout while checking {city} — skipping")
git add .
git commit -m "Update: monitor checkvisaslots for B1/B2 Chennai & Hyderabad"
git push
