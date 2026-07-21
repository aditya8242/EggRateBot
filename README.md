# EggRateBot
Automatically fetches daily Pune egg rates and delivers them to Telegram at a scheduled time — fully automated, free, and reliable.
Built to solve a real business problem: no more manually checking websites every morning.
## 📌 What This Project Does
Scrapes the latest Pune egg rate from
https://www.e2necc.com/home/eggprice
Extracts today’s rates:
- Piece
- Tray
- 100 Eggs
- Peti

Sends the formatted rate as a Telegram message

Runs automatically every ~15 minutes, triggered externally to keep GitHub Actions active

Automatically adds new subscribers when they message /start — no manual chat_id lookup needed

Supports /rate for on-demand checks anytime
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
- GitHub Actions (`workflow_dispatch`)
- cron-job.org (free external scheduler, ~15 min interval)
No databases. No frameworks. No overengineering.
## 📂 Project Structure
```
egg-rate-bot/
│
├── main.py                  # Core script
├── subscribers.json         # Auto-managed list of chat_ids + Telegram update offset
├── README.md                # Documentation
└── .github/
    └── workflows/
        └── egg_rate.yml     # GitHub Actions workflow (manually/externally triggered)
```
## ⚙️ How It Works (High Level)
An external scheduler (cron-job.org) calls GitHub's API roughly every 15 minutes to trigger the workflow
Python script:
- Polls Telegram for new /start and /rate messages, replies accordingly
- Auto-adds any new chat_id from /start to subscribers.json (committed back to the repo)
- Fetches the webpage
- Parses the HTML table
- Finds today’s date
- Extracts rates
- Broadcasts once per day, the first run where NECC's rate is actually available
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
4. No manual chat_id lookup needed — the bot detects /start automatically and adds them within ~15 minutes
## 🔐 Environment Variables (Required)
This project uses GitHub Secrets — no credentials are hardcoded.
Add the following Repository Secrets:
```
Name                Description
TELEGRAM_BOT_TOKEN  Your Telegram bot token
TELEGRAM_CHAT_IDS   Comma-separated chat IDs (e.g. id1,id2)
```
## ⏰ Automation (External Trigger via cron-job.org)
GitHub Actions' built-in `schedule` cron auto-disables after 60 days of repo inactivity. To avoid that (and avoid noisy daily commits just to keep it "active"), this project uses:

- The workflow is set to trigger only on `workflow_dispatch` (no `schedule:` block)
- A free cron service ([cron-job.org](https://cron-job.org)) sends a `POST` request every ~15 minutes to GitHub's Workflow Dispatch API:
```
https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_file}/dispatches
```
with a GitHub Personal Access Token (`repo` scope) in the `Authorization` header and `{"ref": "main"}` as the body.

You can also trigger it manually anytime using **Run workflow** in the GitHub Actions tab.
## 🧪 Manual Testing
Before relying on automation:
python main.py
You should receive a Telegram message immediately.
If manual run works → the scheduled trigger will work.
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

Note: /start and /rate replies arrive within ~15 minutes (polling interval), not instantly — the bot is honest about this in its own messages.
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
