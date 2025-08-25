# 📚 Telegram Study Reminder Bot

A simple yet powerful Telegram bot designed to help students **avoid distractions** and stay on track with their study schedule by sending timely, customizable reminders.

---

## ➡️ Access the Bot

You can interact with the live version of this bot on Telegram:

### **[t.me/studyremainderbot](https://t.me/studyremainderbot)**

---

## ✨ Features

- **Interactive Setup:** No need to type complex commands. Set reminders entirely through inline buttons.
- **Flexible Scheduling:** Choose specific days of the week for your reminders:
  - Every Day
  - Weekdays (Mon-Fri)
  - Mon-Thu
  - Weekends (Sat & Sun)
  - Individual days (Sat, Sun)
- **Precise Timing:** Select the exact hour of the day for the reminder, organized by Morning, Afternoon, Evening, and Night.
- **Customizable Messages:** Set your own personal study reminder message via the `/settings` menu.
- **Easy Management:** View and delete your active reminders at any time.
- **Persistent Storage:** Powered by a Supabase (PostgreSQL) database, your reminders are safely stored and will never be lost, even if the bot restarts.

---

## 🛠️ Technology Stack

- **Language:** Python 3
- **Telegram Library:** `python-telegram-bot`
- **Database:** Supabase (Free Tier PostgreSQL)
- **Hosting:** Render (Free Tier)

---

## 🚀 Getting Started

Follow these instructions to get a copy of the bot up and running for your own use.

### Prerequisites

- Python 3.8 or higher
- A Telegram account
- A Supabase account (free)
- A Render account (free)
- Git

### 1. Set Up the Bot on Telegram

1.  Start a chat with [@BotFather](https://t.me/BotFather) on Telegram.
2.  Use the `/newbot` command to create a new bot.
3.  Follow the instructions and BotFather will give you a unique **API Token**. Save this token.

### 2. Set Up the Supabase Database

1.  Go to [Supabase.com](https://supabase.com) and create a new project.
2.  Go to the **SQL Editor** and run the SQL query found in the `schema.sql` file of this repository to create the `reminders` table.
3.  Go to **Project Settings > API**. Find and save your **Project URL** and your `anon` `public` **API Key**.

### 3. Local Setup & Running

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/MutmainX/StudyRemainderBot.git
    cd StudyRemainderBot
    ```

2.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure your environment variables:**
    It is crucial **not** to write your secret keys directly in the code. This project is set up to read them from environment variables.

    Create a file named `.env` in the project root and add your keys:
    ```
    TELEGRAM_TOKEN="YOUR_TELEGRAM_BOT_TOKEN_HERE"
    SUPABASE_URL="YOUR_SUPABASE_URL_HERE"
    SUPABASE_KEY="YOUR_SUPABASE_ANON_KEY_HERE"
    ```
    *Note: You will need to add `python-dotenv` to your `requirements.txt` and load it in `bot.py` for this to work locally.*

4.  **Run the bot locally:**
    ```bash
    python bot.py
    ```

---

## ☁️ Deployment to Render (24/7 Hosting)

1.  **Push your code to a GitHub repository.** Make sure your `.env` file is listed in your `.gitignore` file so you don't commit your secrets!

2.  **Create a new "Web Service" on Render** and connect it to your GitHub repository.

3.  **Use the following settings:**
    - **Runtime:** `Python 3`
    - **Build Command:** `pip install -r requirements.txt`
    - **Start Command:** `python bot.py`

4.  **Add your secrets** in the **"Environment"** section of the Render dashboard.
    - `TELEGRAM_TOKEN`
    - `SUPABASE_URL`
    - `SUPABASE_KEY`

5.  Deploy! Render will automatically build and run your bot, which will now be online 24/7.

---

