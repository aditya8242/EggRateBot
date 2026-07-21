import requests
from bs4 import BeautifulSoup
from datetime import date
import os
import json

URL = "https://www.e2necc.com/home/eggprice"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ENV_CHAT_IDS = os.environ.get("TELEGRAM_CHAT_IDS", "").split(",")
CITY_NAME = "Pune"
SUBSCRIBERS_FILE = "subscribers.json"

WELCOME_TEXT = (
    "🥚 Welcome! You're subscribed to daily Pune egg rates.\n"
    "Rates are checked throughout the day and sent as soon as NECC updates them "
    "(usually by early afternoon). You'll get today's rate automatically once it's live.\n"
    "Send /rate anytime to check right now."
)

NOT_READY_TEXT = "Today's rate isn't updated by NECC yet. I'll broadcast it automatically the moment it's live."


def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"chat_ids": [], "offset": 0, "last_broadcast_date": None}

    data.setdefault("last_broadcast_date", None)

    for cid in ENV_CHAT_IDS:
        cid = cid.strip()
        if cid and cid not in data["chat_ids"]:
            data["chat_ids"].append(cid)

    return data


def save_subscribers(data):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=10)
    except Exception:
        pass


def broadcast_message(message, chat_ids):
    for chat_id in chat_ids:
        send_telegram_message(TELEGRAM_BOT_TOKEN, chat_id, message)


def fetch_today_rate():
    """Returns formatted message string, or None if not available/failed."""
    today = date.today()
    today_str = today.strftime("%d-%m-%Y")
    day_index = today.day

    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    tbody = soup.find("tbody")
    if not tbody:
        return None

    for row in tbody.find_all("tr"):
        cells = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cells) < 2 or cells[0] != CITY_NAME:
            continue
        if day_index >= len(cells):
            return None
        raw_value = cells[day_index]
        if raw_value in ("-", "", None):
            return None
        try:
            price_100 = float(raw_value)
        except ValueError:
            return None

        piece = round(price_100 / 100, 2)
        tray = round(piece * 30, 2)
        peti = round(piece * 210, 2)

        return (
            f"🥚 Egg Rate – {CITY_NAME}\n"
            f"Date: {today_str}\n"
            f"Piece: ₹{piece}\n"
            f"Tray (30): ₹{tray}\n"
            f"100 Eggs: ₹{price_100}\n"
            f"Peti (210): ₹{peti}"
        )
    return None


def handle_updates(data):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    try:
        resp = requests.get(url, params={"offset": data["offset"], "timeout": 0}, timeout=10)
        resp.raise_for_status()
        updates = resp.json().get("result", [])
    except Exception:
        return data

    changed = False
    max_update_id = data["offset"] - 1

    for update in updates:
        update_id = update.get("update_id")
        if update_id is not None and update_id > max_update_id:
            max_update_id = update_id

        message = update.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")
        if chat_id is None:
            continue
        chat_id_str = str(chat_id)

        if text == "/start":
            if chat_id_str not in data["chat_ids"]:
                data["chat_ids"].append(chat_id_str)
                changed = True
            send_telegram_message(TELEGRAM_BOT_TOKEN, chat_id_str, WELCOME_TEXT)

        elif text == "/rate":
            rate_msg = fetch_today_rate()
            send_telegram_message(TELEGRAM_BOT_TOKEN, chat_id_str, rate_msg or NOT_READY_TEXT)

    if max_update_id >= data["offset"]:
        data["offset"] = max_update_id + 1
        changed = True

    if changed:
        save_subscribers(data)

    return data


def main():
    data = load_subscribers()
    data = handle_updates(data)

    today_str = date.today().isoformat()
    if data.get("last_broadcast_date") == today_str:
        return  # already broadcast today, nothing more to do this run

    rate_msg = fetch_today_rate()
    if rate_msg is None:
        return  # not available yet, next run will check again

    broadcast_message(rate_msg, data["chat_ids"])
    data["last_broadcast_date"] = today_str
    save_subscribers(data)


if __name__ == "__main__":
    main()
