import requests
from bs4 import BeautifulSoup
from datetime import date
import os
import json

# ================= CONFIG =================
URL = "https://www.e2necc.com/home/eggprice"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ENV_CHAT_IDS = os.environ.get("TELEGRAM_CHAT_IDS", "").split(",")
CITY_NAME = "Pune"
SUBSCRIBERS_FILE = "subscribers.json"
# ==========================================

def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"chat_ids": [], "offset": 0}

    # fold in any chat_ids from the old env var secret, one-time migration
    for cid in ENV_CHAT_IDS:
        cid = cid.strip()
        if cid and cid not in data["chat_ids"]:
            data["chat_ids"].append(cid)

    return data

def save_subscribers(data):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def check_new_subscribers(data):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {"offset": data["offset"], "timeout": 0}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        updates = resp.json().get("result", [])
    except Exception:
        return data  # if Telegram polling fails, just skip discovery this run

    changed = False
    max_update_id = data["offset"] - 1

    for update in updates:
        update_id = update.get("update_id")
        if update_id is not None and update_id > max_update_id:
            max_update_id = update_id

        message = update.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")

        if text == "/start" and chat_id is not None:
            chat_id_str = str(chat_id)
            if chat_id_str not in data["chat_ids"]:
                data["chat_ids"].append(chat_id_str)
                changed = True

    if max_update_id >= data["offset"]:
        data["offset"] = max_update_id + 1
        changed = True

    if changed:
        save_subscribers(data)

    return data

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        resp = requests.post(url, data=payload, timeout=10)
        resp.raise_for_status()
    except Exception:
        pass  # one bad chat_id shouldn't kill the whole broadcast

def broadcast_message(message, chat_ids):
    for chat_id in chat_ids:
        send_telegram_message(TELEGRAM_BOT_TOKEN, chat_id, message)

def main():
    data = load_subscribers()
    data = check_new_subscribers(data)
    chat_ids = data["chat_ids"]

    today = date.today()
    today_str = today.strftime("%d-%m-%Y")
    day_index = today.day

    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
    except Exception:
        broadcast_message("Egg rate unavailable today (site not reachable)", chat_ids)
        return

    soup = BeautifulSoup(response.text, "html.parser")
    tbody = soup.find("tbody")
    if not tbody:
        broadcast_message("Egg rate unavailable today (table not found)", chat_ids)
        return

    rows = tbody.find_all("tr")
    for row in rows:
        cells = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cells) < 2:
            continue
        if cells[0] == CITY_NAME:
            if day_index >= len(cells):
                broadcast_message(f"Egg rate unavailable today (day column out of range for {today_str})", chat_ids)
                return

            raw_value = cells[day_index]
            if raw_value in ("-", "", None):
                broadcast_message(f"Egg rate unavailable today (NECC hasn't updated {today_str} yet)", chat_ids)
                return

            try:
                price_100 = float(raw_value)
            except ValueError:
                broadcast_message(f"Egg rate unavailable today (unexpected value '{raw_value}')", chat_ids)
                return

            piece = round(price_100 / 100, 2)
            tray = round(piece * 30, 2)
            peti = round(piece * 210, 2)

            message = (
                f"🥚 Egg Rate – {CITY_NAME}\n"
                f"Date: {today_str}\n"
                f"Piece: ₹{piece}\n"
                f"Tray (30): ₹{tray}\n"
                f"100 Eggs: ₹{price_100}\n"
                f"Peti (210): ₹{peti}"
            )
            broadcast_message(message, chat_ids)
            return

    broadcast_message(f"Egg rate unavailable today ({CITY_NAME} row not found)", chat_ids)

if __name__ == "__main__":
    main()
