# 📚 Telegram Study Reminder Bot


## A simple yet powerful Telegram bot designed to help students **avoid distractions** and stay on track with their study schedule by sending timely, customizable reminders.


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
2.  Go to the **SQL Editor** and run the SQL query found in the `supabase table` file of this repository to create the `reminders` table.
3.  Go to **Project Settings > API**. Find and save your **Project URL** and your `anon` `public` **API Key**.

### 3. Local Setup & Running

1.  **Clone the repository or download zip file:**
    ```bash
    git clone https://github.com/MutmainX/StudyRemainderBot.git
    cd StudyRemainderBot
    ```

2.  **Install the required libraries from requirements.txt:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Replace with keys :**
SUPABASE_URL = "replace with your SUPABASE_URL"  
SUPABASE_KEY = "Add your supabase url here" 
TELEGRAM_TOKEN = "replace with your TELEGRAM_TOKEN"  
6.  

7.  **Run the bot locally:**
    ```bash
    python bot.py
    ```

---

### ☁️ You can deploy it with Replit for free

Create new py project there
Paste the Code
Install dependecies
Add keys in Secrets
Deploy

