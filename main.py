import requests
from bs4 import BeautifulSoup
from datetime import date
import os

# ================= CONFIG =================
URL = "https://www.e2necc.com/home/eggprice"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_IDS = os.environ.get("TELEGRAM_CHAT_IDS", "").split(",")
CITY_NAME = "Pune"
# ==========================================

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    requests.post(url, data=payload, timeout=10)

def broadcast_message(message):
    for chat_id in TELEGRAM_CHAT_IDS:
        send_telegram_message(
            TELEGRAM_BOT_TOKEN,
            chat_id,
            message
        )

def main():
    today = date.today()
    today_str = today.strftime("%d-%m-%Y")
    day_index = today.day  # column position for today's rate

    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
    except Exception:
        broadcast_message(
            "Egg rate unavailable today (site not reachable)"
        )
        return

    soup = BeautifulSoup(response.text, "html.parser")
    tbody = soup.find("tbody")
    if not tbody:
        broadcast_message(
            "Egg rate unavailable today (table not found)"
        )
        return

    rows = tbody.find_all("tr")
    for row in rows:
        cells = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cells) < 2:
            continue
        if cells[0] == CITY_NAME:
            # cells[0] = city, cells[1..31] = day 1..31, cells[32] = average
            if day_index >= len(cells):
                broadcast_message(
                    f"Egg rate unavailable today (day column out of range for {today_str})"
                )
                return

            raw_value = cells[day_index]
            if raw_value in ("-", "", None):
                broadcast_message(
                    f"Egg rate unavailable today (NECC hasn't updated {today_str} yet)"
                )
                return

            try:
                price_100 = float(raw_value)
            except ValueError:
                broadcast_message(
                    f"Egg rate unavailable today (unexpected value '{raw_value}')"
                )
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
            broadcast_message(message)
            return

    broadcast_message(
        f"Egg rate unavailable today ({CITY_NAME} row not found)"
    )

if __name__ == "__main__":
    main()
