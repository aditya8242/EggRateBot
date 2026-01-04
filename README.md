# EggRateBot

Automatically fetches daily Pune egg rates and delivers them to Telegram at a scheduled time — fully automated, free, and reliable.

Built to solve a real business problem: no more manually checking websites every morning.

## 📌 What This Project Does

Scrapes the latest Pune egg rate from
https://todayeggrate.in/pune-egg-rate/

Extracts today’s rates:
- Piece
- Tray
- 100 Eggs
- Peti

Sends the formatted rate as a Telegram message
Runs automatically every day using GitHub Actions (cron)

## 🧠 Why This Exists

* Saves time for small egg businesses
* Eliminates daily manual checking
* Works without paid servers
* Runs even when your laptop is off

### Designed to be:

- Simple
- Defensive
- Low maintenance

## 🏗️ Tech Stack

- Python 3
- requests
- beautifulsoup4
- Telegram Bot API
- GitHub Actions (free cron)

No databases. No frameworks. No overengineering.

## 📂 Project Structure
```
egg-rate-bot/
│
├── main.py                  # Core script
├── README.md                # Documentation
└── .github/
    └── workflows/
        └── egg_rate.yml     # GitHub Actions cron job
```
## ⚙️ How It Works (High Level)

GitHub Actions triggers the workflow at a fixed time

Python script:
- Fetches the webpage
- Parses the HTML table
- Finds today’s date
- Extracts rates
- Sends the result to one or more Telegram users
- If anything fails → sends a clear failure message
- No silent failures.

## 🤖 Telegram Bot Setup (One-Time)

1. Open Telegram
2. Search @BotFather
3. Create a new bot using /newbot
4. Save the Bot Token

- Each recipient must:

1. Open the bot
2. Press Start once
3. Telegram bots cannot message users who haven’t started the bot

## 🔐 Environment Variables (Required)

This project uses GitHub Secrets — no credentials are hardcoded.

Add the following Repository Secrets:
```
Name                Description
TELEGRAM_BOT_TOKEN  Your Telegram bot token
TELEGRAM_CHAT_IDS   Comma-separated chat IDs (e.g. id1,id2)
```
⏰ Automation (GitHub Actions Cron)

The bot runs automatically using this cron schedule:

`cron: "0 7 * * *"`


⏱️ Runs at 12:30 PM IST
(GitHub Actions uses UTC)

You can also trigger it manually using Run workflow in GitHub Actions.

## 🧪 Manual Testing

Before relying on automation:

python main.py

You should receive a Telegram message immediately.

If manual run works → cron will work.

## 📤 Message Format

Example:
```
🥚 Egg Rate – Pune
Date: 03-01-2026
Piece: ₹6.5
Tray: ₹195
100 Eggs: ₹650
Peti: ₹1950
```

If data is unavailable:

Egg rate unavailable today (site not reachable)

## 🛡️ Failure Handling

This project never sends incorrect data.

Handled safely:

- Website down
- HTML structure changes
- Today’s date missing
- Network errors
- All failures result in a clear Telegram message.

## 🚫 What This Project Does NOT Do

❌ WhatsApp automation (paid / restricted)

❌ Store historical data

❌ Use databases

❌ Overengineer simple automation

## Author
Aditya Chavan
