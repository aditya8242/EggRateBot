import requests
from bs4 import BeautifulSoup
from datetime import date

# ================= CONFIG =================
URL = "https://todayeggrate.in/pune-egg-rate/"
import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_IDS = os.environ.get("TELEGRAM_CHAT_IDS", "").split(",")

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
    today_str = date.today().strftime("%d-%m-%Y")

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

        if len(cells) < 5:
            continue

        if cells[0] == today_str:
            message = (
                f"🥚 Egg Rate – Pune\n"
                f"Date: {cells[0]}\n"
                f"Piece: {cells[1]}\n"
                f"Tray: {cells[2]}\n"
                f"100 Eggs: {cells[3]}\n"
                f"Peti: {cells[4]}"
            )

            broadcast_message(message)
            return

    broadcast_message(
        "Egg rate unavailable today (today's date not listed)"
    )


if __name__ == "__main__":
    main()
