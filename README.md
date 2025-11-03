ReminderBot

A Telegram bot built with aiogram, providing multilingual support, time-zone aware reminders, and Redis + SQLAlchemy for storage and state management.

🧩 Features

Register user with location to detect time zone

Set one-time reminders with time zone conversion (e.g., /remind Do something; 04.11 18:00)

Store reminders in UTC internally and send at the correct local time

View a list of active reminders (/remind_list)

Delete a reminder by its ID (/dell_remind <id>)

Change interface language (/language) – available languages: English, Russian, Ukrainian

/help command to show usage instructions in the user’s language

🚀 Getting Started
Prerequisites

Python 3.10+

Redis server

PostgreSQL or SQLite (depending on your db setup)

A Telegram bot token from BotFather

Setup

Clone the repo:

git clone https://github.com/younici/ReminderBot.git
cd ReminderBot


Create a .env file in the root directory with the following variables:

BOT_TOKEN=your_telegram_bot_token
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite+aiosqlite:///./db.sqlite3   # Or your PostgreSQL URL


Install dependencies:

pip install -r requirements.txt


Setup database (run migrations or use your ORM’s create-tables logic).

Make sure Redis is running:

redis-server


Start the bot:

python main.py

🗂️ How to Use

/start: Begin registration. The bot will ask for your location to detect your time zone.

/remind <text>; dd.mm HH:MM: Create a reminder scheduled for the given local date and time.

/remind_list: List your active (not yet sent) reminders with IDs and schedule times.

/dell_remind <id>: Delete a specific reminder by its ID.

/language: Change your interface language.

/help: Get a list of available commands in your language.

🧠 How It Works

User location is collected once to determine their IANA time zone using timezonefinder.

Reminders are converted to UTC when saved, so they fire at the correct time regardless of DST or server location.

Redis is used to store session data (language preference) and optionally caching.

SQLAlchemy with async sessions is used for storage of users and reminders, with proper relationships (User.remind_list) and time-zone aware logic.

🛠️ Configuration Notes

Ensure your tzdata package is available to support zoneinfo.

In .po files you have multilingual strings — for example "HELP_ANSWER" key holds the command list in each language.

Use proper locale fallback logic if user’s language isn’t found: default to en.

When scheduling reminders, ensure user time is strictly in the future relative to their time zone.

✅ To-Do / Future Improvements

Show human‐friendly formatted time in /remind_list, including time zone label.

Add inline keyboard actions for deletion of reminders (instead of text command).

Support recurring reminders (daily, weekly).

Add message attachments (images/audio) to reminders.

Add better error handling and user feedback (e.g., invalid time format, missing commands).
