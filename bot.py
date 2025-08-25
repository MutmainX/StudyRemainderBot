import logging
import os
from datetime import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from supabase import create_client, Client

# paste your keys here---

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_KEY']
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']


# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Enable logging to see errors
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# States for the conversation handlers
(
    SELECTING_DAY,
    SELECTING_PERIOD,
    SELECTING_HOUR,
    CHANGING_MESSAGE,
    DELETING_REMINDER,
) = range(5)

# helper functions for database

# --- NEW CORRECT VERSION ---
async def schedule_reminder(job_queue, chat_id: int, reminder_time: time, days: tuple, message: str, reminder_id: int):
    """Schedules a new reminder job."""
    job_name = f"reminder_{reminder_id}"
    job_queue.run_daily(
        callback=send_reminder,
        time=reminder_time,
        days=days,
        chat_id=chat_id,
        user_id=chat_id, 
        name=job_name,
        data={"message": message}
    )
    logger.info(f"Scheduled job {job_name} for chat {chat_id} at {reminder_time} on days {days}")

async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends the reminder message."""
    job = context.job
    # Fetch the latest message from the database in case it was updated
    response = supabase.table("reminders").select("custom_message").eq("chat_id", job.chat_id).limit(1).execute()
    message = response.data[0]['custom_message'] if response.data else job.data.get("message")
    
    await context.bot.send_message(chat_id=job.chat_id, text=message)
    logger.info(f"Sent reminder to {job.chat_id}")

#  bot commands and converstations

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message."""
    welcome_text = (
        "Welcome! I'm your Study Reminder Bot. 📚\n\n"
        "Use /remind to set a reminder or /settings to manage it."
    )
    await update.message.reply_text(welcome_text)

async def remind_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the /remind conversation and asks for the day."""
    keyboard = [
        [InlineKeyboardButton("🗓️ Every Day", callback_data="all_days")],
        [
            InlineKeyboardButton("M-F", callback_data="weekdays"),
            InlineKeyboardButton("M-Th", callback_data="mon_thu"),
        ],
        [
            InlineKeyboardButton("Sat", callback_data="sat"),
            InlineKeyboardButton("Sun", callback_data="sun"),
            InlineKeyboardButton("Sat & Sun", callback_data="weekend"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("For which days should I set the reminder?", reply_markup=reply_markup)
    return SELECTING_DAY

async def select_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes day selection and asks for the time period."""
    query = update.callback_query
    await query.answer()

    day_map = {
        "all_days": tuple(range(7)),
        "weekdays": tuple(range(5)),
        "mon_thu": tuple(range(4)),
        "sat": (5,),
        "sun": (6,),
        "weekend": (5, 6),
    }
    context.user_data["days"] = day_map[query.data]

    keyboard = [
        [
            InlineKeyboardButton("☀️ Morning", callback_data="morning"),
            InlineKeyboardButton("🌤️ Afternoon", callback_data="afternoon"),
        ],
        [
            InlineKeyboardButton("🌆 Evening", callback_data="evening"),
            InlineKeyboardButton("🌙 Night", callback_data="night"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Great. Now, at what time of day?", reply_markup=reply_markup)
    return SELECTING_PERIOD

async def select_time_period(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes time period and shows specific hours."""
    query = update.callback_query
    await query.answer()

    time_periods = {
        "morning": [f"{h}:00 AM" for h in range(4, 12)],
        "afternoon": [f"{h}:00 PM" for h in [12, 1, 2, 3, 4]],
        "evening": [f"{h}:00 PM" for h in range(5, 9)],
        "night": [f"{h}:00 PM" for h in range(9, 12)] + ["12:00 AM"],
    }
    
    period = query.data
    hours = time_periods[period]
    
    keyboard = [
        [InlineKeyboardButton(hour, callback_data=hour) for hour in hours[i:i+4]]
        for i in range(0, len(hours), 4)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Please select a specific time:", reply_markup=reply_markup)
    return SELECTING_HOUR

async def select_hour(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes the final hour, saves, and confirms."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    chat_id = query.message.chat_id
    selected_time_str = query.data

    # Convert time string to time object
    hour, minute_ampm = selected_time_str.split(':')
    minute, ampm = minute_ampm.split(' ')
    hour = int(hour)
    
    if ampm == 'PM' and hour != 12:
        hour += 12
    if ampm == 'AM' and hour == 12: # Midnight case
        hour = 0

    reminder_time_obj = time(hour, int(minute))
    days_tuple = context.user_data["days"]
    
    # Save to database
    try:
        response = supabase.table("reminders").insert({
            "user_id": user_id,
            "chat_id": chat_id,
            "reminder_time": str(reminder_time_obj),
            "days": [str(d) for d in days_tuple] # Store as array of strings
        }).execute()

        if response.data:
            reminder_id = response.data[0]['id']
            await schedule_reminder(context, chat_id, reminder_time_obj, days_tuple, 'Default message', reminder_id)
            await query.edit_message_text(f"✅ Success! Reminder set for the selected days at {selected_time_str}.")
        else:
            await query.edit_message_text("Sorry, there was an error saving your reminder.")

    except Exception as e:
        logger.error(f"Error saving reminder: {e}")
        await query.edit_message_text("An error occurred. Please try again.")

    context.user_data.clear()
    return ConversationHandler.END

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the settings menu."""
    keyboard = [
        [InlineKeyboardButton("✏️ Change Reminder Message", callback_data="change_msg")],
        [InlineKeyboardButton("🗑️ View/Delete Reminders", callback_data="delete_reminders")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Settings:", reply_markup=reply_markup)

async def change_message_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks the user for a new reminder message."""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Please send me the new reminder message you want to use.")
    return CHANGING_MESSAGE

async def update_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Updates the user's custom message in the database."""
    user_id = update.message.from_user.id
    new_message = update.message.text
    try:
        supabase.table("reminders").update({"custom_message": new_message}).eq("user_id", user_id).execute()
        await update.message.reply_text("✅ Your reminder message has been updated!")
    except Exception as e:
        logger.error(f"Error updating message: {e}")
        await update.message.reply_text("An error occurred while updating your message.")
    return ConversationHandler.END


async def delete_reminders_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows a list of reminders with delete buttons."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    response = supabase.table("reminders").select("*").eq("user_id", user_id).execute()
    if not response.data:
        await query.edit_message_text("You have no active reminders.")
        return

    keyboard = []
    day_map = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for rem in response.data:
        # Format time
        t_obj = time.fromisoformat(rem['reminder_time'])
        time_str = t_obj.strftime("%I:%M %p")
        # Format days
        days_list = [day_map[int(d)] for d in rem['days']]
        days_str = ", ".join(days_list)
        
        button_text = f"❌ {days_str} at {time_str}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"del_{rem['id']}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Click a reminder to delete it:", reply_markup=reply_markup)

async def perform_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Deletes a reminder from the database and the job queue."""
    query = update.callback_query
    await query.answer()
    reminder_id = int(query.data.split("_")[1])
    
    # Remove from Job Queue
    job_name = f"reminder_{reminder_id}"
    jobs = context.job_queue.get_jobs_by_name(job_name)
    for job in jobs:
        job.schedule_removal()
    
    # Remove from Database
    supabase.table("reminders").delete().eq("id", reminder_id).execute()
    
    await query.edit_message_text("✅ Reminder deleted successfully.")
    # Show the updated list
    await delete_reminders_list(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Operation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END


async def reload_jobs_from_db(application: Application):
    """Loads all reminders from DB and schedules them on bot start."""
    logger.info("Reloading jobs from database...")
    response = supabase.table("reminders").select("*").execute()
    if response.data:
        for rem in response.data:
            try:
                chat_id = rem['chat_id']
                reminder_time = time.fromisoformat(rem['reminder_time'])
                days = tuple(int(d) for d in rem['days'])
                message = rem['custom_message']
                reminder_id = rem['id']
                await schedule_reminder(application.job_queue, chat_id, reminder_time, days, message, reminder_id)
            except Exception as e:
                logger.error(f"Failed to reload job {rem.get('id')}: {e}")

# --- NEW CORRECT VERSION ---
async def reload_jobs_from_db(application: Application):
    """Loads all reminders from DB and schedules them on bot start."""
    logger.info("Reloading jobs from database...")
    response = supabase.table("reminders").select("*").execute()
    if response.data:
        for rem in response.data:
            try:
                chat_id = rem['chat_id']
                reminder_time = time.fromisoformat(rem['reminder_time'])
                days = tuple(int(d) for d in rem['days'])
                message = rem['custom_message']
                reminder_id = rem['id']
                # Pass the job_queue directly from the application object
                await schedule_reminder(application.job_queue, chat_id, reminder_time, days, message, reminder_id)
            except Exception as e:
                logger.error(f"Failed to reload job {rem.get('id')}: {e}")
                
def main() -> None:
    """Run the bot."""
    # The new post_init parameter tells the bot to run our function AFTER it's ready
    application = Application.builder().token(TELEGRAM_TOKEN).post_init(reload_jobs_from_db).build()

    # Conversation handler for setting reminders
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("remind", remind_start)],
        states={
            SELECTING_DAY: [CallbackQueryHandler(select_day)],
            SELECTING_PERIOD: [CallbackQueryHandler(select_time_period)],
            SELECTING_HOUR: [CallbackQueryHandler(select_hour)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Conversation handler for changing message
    msg_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(change_message_prompt, pattern="^change_msg$")],
        states={
            CHANGING_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_message)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(conv_handler)
    application.add_handler(msg_handler)
    application.add_handler(CallbackQueryHandler(delete_reminders_list, pattern="^delete_reminders$"))
    application.add_handler(CallbackQueryHandler(perform_delete, pattern="^del_"))
    

    application.run_polling(drop_pending_updates=True) # Also keeping this from before

if __name__ == "__main__":

    main()
