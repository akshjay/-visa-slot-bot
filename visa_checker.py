import os
import sys
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

URL = "https://checkvisaslots.com/visa-slots-info/in/b1-b2-regular/"
CITIES = ["chennai", "hyderabad"]

def send_telegram(message):
    import requests
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)

def is_fresh(time_str):
    # Fresh = minutes ago or 1-2 hours ago
    time_str = time_str.lower().strip()
    if re.match(r"\d+m ago", time_str):
        return True
    if re.match(r"1h ago", time_str):
        return True
    if re.match(r"2h ago", time_str):
        return True
    return False

def check_slots():
    fresh_slots = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = browser.new_context()
        page = context.new_page()

        try:
            print("Loading checkvisaslots.com...")
            page.goto(URL, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=15000)

            content = page.content().lower()

            # Look for patterns like "chennai • 5m ago" or "hyderabad • 1h ago"
            for city in CITIES:
                # Find all occurrences of city followed by time
                matches = re.findall(
                    rf"{city}\s*[•·]\s*(\d+m ago|\d+h ago|< \d+ hours ago)",
                    content
                )
                print(f"{city.title()} recent times found: {matches}")

                for match in matches:
                    if is_fresh(match):
                        fresh_slots.append((city.title(), match))
                        print(f"🚨 FRESH SLOT: {city.title()} — {match}")
                    else:
                        print(f"{city.title()} last slot was: {match} — not fresh")

        except PlaywrightTimeout:
            print("Timeout loading page — skipping")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

    return fresh_slots

def main():
    print("Visa slot checker starting...")

    if not BOT_TOKEN or not CHAT_ID:
        print("BOT_TOKEN or CHAT_ID not set")
        sys.exit(1)

    fresh_slots = check_slots()

    if fresh_slots:
        for city, time_ago in fresh_slots:
            send_telegram(
                f"🚨 FRESH B1/B2 VISA SLOT in {city}!\n"
                f"Seen: {time_ago}\n"
                f"Book NOW: https://www.usvisascheduling.com"
            )
        print(f"Alert sent for: {fresh_slots}")
    else:
        print("No fresh slots found. No alert sent.")

    print("Check complete. Exiting.")
    sys.exit(0)

if __name__ == "__main__":
    main()
