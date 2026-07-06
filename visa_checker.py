import os
import sys
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

URL = "https://checkvisaslots.com/visa-slots-info/in/b1-b2-regular/"

def send_telegram(message):
    import requests
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)

def check_slots():
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

            # Print raw visible text so we can see exact format
            content = page.inner_text("body")
            print("=== PAGE TEXT START ===")
            print(content[:3000])
            print("=== PAGE TEXT END ===")

        except PlaywrightTimeout:
            print("Timeout loading page")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

def main():
    print("Visa slot checker starting...")
    if not BOT_TOKEN or not CHAT_ID:
        print("BOT_TOKEN or CHAT_ID not set")
        sys.exit(1)
    check_slots()
    print("Check complete. Exiting.")
    sys.exit(0)

if __name__ == "__main__":
    main()
