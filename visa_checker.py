import os
import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

URLS = {
    "Chennai": "https://checkvisaslots.com/visa-slots-info/in/b1-b2-regular/",
    "Hyderabad": "https://checkvisaslots.com/visa-slots-info/in/b1-b2-regular/",
}

KEYWORDS_UNAVAILABLE = ["no slots", "no appointments", "not available", "unavailable"]
KEYWORDS_AVAILABLE = ["chennai", "hyderabad", "available", "slots found"]

def send_telegram(message):
    import requests
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)

def check_slots():
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
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
                    results[city] = None
                print(f"{city}: {'SLOT FOUND' if results[city] else 'No slot'}")
            except PlaywrightTimeout:
                print(f"Timeout while checking {city} - skipping")
                results[city] = None
            except Exception as e:
                print(f"Error checking {city}: {e}")
                results[city] = None
        browser.close()
    return results

def main():
    print("Visa slot checker starting...")
    if not BOT_TOKEN or not CHAT_ID:
        print("BOT_TOKEN or CHAT_ID not set")
        sys.exit(1)
    results = check_slots()
    found_any = False
    for city, available in results.items():
        if available is True:
            send_telegram(f"VISA SLOT AVAILABLE in {city}! Book now!\n{URLS[city]}")
            found_any = True
    if not found_any:
        print("No slots found. No Telegram message sent.")
    print("Check complete. Exiting.")
    sys.exit(0)

if __name__ == "__main__":
    main()
