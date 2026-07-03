import time
from datetime import datetime
from playwright.sync_api import sync_playwright
import requests

BOT_TOKEN = "8746011664:AAEJYvYe7euO4_VeqAowfJ_BLCVZ3FokPss"
CHAT_ID = "8152856153"

CHECK_INTERVAL = 60  # 60 seconds

state = {
    "chennai": False,
    "hyderabad": False
}


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


def check_page():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = "https://www.usvisaslotsinfo.com/visa/b1-b2"
        page.goto(url, timeout=60000)

        # wait for content to load properly
        page.wait_for_timeout(5000)

        content = page.content().lower()

        browser.close()

        # 🔴 STRICT detection rules (avoid false positives)

        chennai_flag = False
        hyderabad_flag = False

        # look for structured indicators, not just "available"
        if "chennai" in content:
            if "available" in content or "slots" in content:
                # extra safety: ensure it's not just page header text
                chennai_flag = "chennai" in content.split("available")[-1][:200]

        if "hyderabad" in content:
            if "available" in content or "slots" in content:
                hyderabad_flag = "hyderabad" in content.split("available")[-1][:200]

        return chennai_flag, hyderabad_flag


def evaluate():
    global state

    try:
        chennai, hyderabad = check_page()

        alerts = []

        if chennai and not state["chennai"]:
            alerts.append("🚨 B1/B2 SLOT AVAILABLE IN CHENNAI")

        if hyderabad and not state["hyderabad"]:
            alerts.append("🚨 B1/B2 SLOT AVAILABLE IN HYDERABAD")

        state["chennai"] = chennai
        state["hyderabad"] = hyderabad

        return alerts

    except Exception as e:
        return [f"⚠️ Error checking slots: {e}"]


send_message("🚀 Visa bot started (Playwright mode)")
print("Bot running...")


def main():
    chennai, hyderabad = check_slots()

    print(f"Chennai={chennai} Hyderabad={hyderabad}")

    if chennai or hyderabad:
        send_message(f"🚨 Slot found!\nChennai: {chennai}\nHyderabad: {hyderabad}")
    else:
        print("No slots found")

if __name__ == "__main__":
    main()
