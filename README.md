ReminderBot

A Telegram bot built with aiogram, providing multilingual support, time-zone aware reminders, and Redis + SQLAlchemy for storage and state management.

🧩 Features

Register user by manually providing time zone (IANA name)

Set one-time reminders with time zone conversion (e.g., /remind Do something; 04.11 18:00)

Store reminders in UTC internally and send at the correct local time

View a list of active reminders (/remind_list)

Delete a reminder by its ID (/dell_remind <id>)

Free plan limited to 3 active reminders; Telegram Stars subscription unlocks unlimited

Inline button menu for all actions (create, list, delete, time zone, language, subscribe)

Change interface language (/language) – available languages: English, Russian, Ukrainian

/help command to show usage instructions in the user’s language

🚀 Getting Started
Prerequisites

Python 3.10+

Redis server

PostgreSQL or SQLite (depending on your db setup)

A Telegram bot token from BotFather
Telegram Stars provider token (for payments)

Setup

Clone the repo:

git clone https://github.com/younici/ReminderBot.git
cd ReminderBot


Create a .env file in the root directory with the following variables:

BOT_TOKEN=your_telegram_bot_token
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite+aiosqlite:///./db.sqlite3
 # Or your PostgreSQL URL
STARS_PROVIDER_TOKEN=your_telegram_stars_provider_token
# Optional overrides
FREE_REMINDER_LIMIT=3
SUBSCRIPTION_PRICE_STARS=50
SUBSCRIPTION_DURATION_DAYS=30
SUBSCRIPTION_TITLE="ReminderBot Premium"
SUBSCRIPTION_DESCRIPTION="Unlimited reminders for 30 days. Paid with Telegram Stars."


Install dependencies:

pip install -r requirements.txt


Setup database (run migrations or use your ORM’s create-tables logic).

Make sure Redis is running:

redis-server


Start the bot:

python main.py

🐳 Docker (app + Redis)

Build and run with Docker Compose:

```
docker compose up -d --build
```

Env vars are read from `.env`; Redis URL defaults to `redis://redis:6379/0`. SQLite data is persisted in `./DataBase` (mounted into the container).

🚀 One-command deploy

Use the provided script to clone/pull from GitHub and start in Docker:

```
REPO_URL=https://github.com/younici/ReminderBot.git APP_DIR=/opt/reminderbot bash deploy.sh
```

Edit `.env` after the first run (auto-copied from `.env.example`) and rerun `docker compose up -d` if needed.

🗂️ How to Use

/start: Begin registration. The bot will ask for your IANA time zone (e.g., Europe/Kyiv).

/menu: Open the inline menu with buttons for all actions.

/timezone: Change your time zone.

/remind <text>; dd.mm HH:MM: Create a reminder scheduled for the given local date and time.

/remind_list: List your active (not yet sent) reminders with IDs and schedule times.

/dell_remind <id>: Delete a specific reminder by its ID.

/subscribe: Buy unlimited reminders with Telegram Stars (default 30-day subscription).

/language: Change your interface language.

/help: Get a list of available commands in your language.

🧠 How It Works

User supplies their time zone once; reminders use that zone and convert to UTC internally.

Reminders are converted to UTC when saved, so they fire at the correct time regardless of DST or server location.

Redis is used only for FSM/state storage.

SQLAlchemy with async sessions is used for storage of users and reminders, with proper relationships (User.remind_list) and time-zone aware logic.

🛠️ Configuration Notes

Ensure your tzdata package is available to support zoneinfo.

In .po files you have multilingual strings — for example "HELP_ANSWER" key holds the command list in each language.

Use proper locale fallback logic if user’s language isn’t found: default to en.

When scheduling reminders, ensure user time is strictly in the future relative to their time zone.

Telegram Stars is used for subscriptions: invoice currency is XTR. The free plan allows 3 active reminders; premium removes the cap.

✅ To-Do / Future Improvements

Show human‐friendly formatted time in /remind_list, including time zone label.

Add inline keyboard actions for deletion of reminders (instead of text command).

Support recurring reminders (daily, weekly).

Add message attachments (images/audio) to reminders.

Add better error handling and user feedback (e.g., invalid time format, missing commands).
