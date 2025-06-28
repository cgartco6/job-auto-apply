import os
import logging
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    ContextTypes
)
from config import config
from database.job_tracker import JobTracker
from utils.file_utils import FileManager

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.job_tracker = JobTracker()
        
        # Register handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("stats", self.stats))
        self.application.add_handler(CommandHandler("stop", self.stop))
        self.application.add_handler(CommandHandler("resume", self.resume))
        self.application.add_handler(CommandHandler("status", self.status))
        self.application.add_handler(CommandHandler("get_cv", self.get_cv))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Set bot commands
        commands = [
            BotCommand("start", "Start the job search bot"),
            BotCommand("stats", "Get application statistics"),
            BotCommand("stop", "Pause job searching"),
            BotCommand("resume", "Resume job searching"),
            BotCommand("status", "Current search status"),
            BotCommand("get_cv", "Get current CV version")
        ]
        self.application.bot.set_my_commands(commands)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        await update.message.reply_html(
            rf"Hi {user.mention_html()}! I'm your Job Search Assistant.",
            reply_markup=self.get_main_keyboard()
        )
        await self.send_welcome_message(update)
    
    async def send_welcome_message(self, update: Update):
        message = (
            "🚀 *Job Search Bot Activated*\n\n"
            "I'll help you with:\n"
            "• Finding relevant jobs in South Africa\n"
            "• Customizing your CV for each position\n"
            "• Sending applications automatically\n"
            "• Tracking your applications\n\n"
            "Use /stats to see your progress or /stop to pause searching."
        )
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send application statistics"""
        stats = self.job_tracker.get_stats()
        message = (
            f"📊 *Application Statistics*\n\n"
            f"• Total Applications: {stats['total']}\n"
            f"• Successful: {stats['successful']}\n"
            f"• Failed: {stats['failed']}\n"
            f"• Pending: {stats['pending']}\n"
            f"• Offers: {stats['offers']}\n\n"
            f"⏱ Last Application: {stats['last_application']}"
        )
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Pause job searching"""
        # Implement pause logic in main system
        await update.message.reply_text(
            "⏸ Job searching paused. Use /resume to continue."
        )
    
    async def resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Resume job searching"""
        # Implement resume logic in main system
        await update.message.reply_text(
            "▶️ Job searching resumed. I'll notify you of new opportunities."
        )
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Get current search status"""
        status = "Active"  # Should come from main system
        last_job = "Python Developer at TechCorp"
        message = (
            f"🔍 *Current Search Status*\n\n"
            f"• Status: {status}\n"
            f"• Locations: Cape Town, Johannesburg, Remote\n"
            f"• Last Job Applied: {last_job}\n"
            f"• Next Search In: 15 minutes"
        )
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def get_cv(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send current CV to user"""
        try:
            cv_path = config.BASE_CV_PDF if os.path.exists(config.BASE_CV_PDF) else None
            if cv_path:
                await update.message.reply_document(
                    document=open(cv_path, 'rb'),
                    caption="Here's your current CV"
                )
            else:
                await update.message.reply_text("CV file not found.")
        except Exception as e:
            logger.error(f"Error sending CV: {str(e)}")
            await update.message.reply_text("Couldn't retrieve CV. Please try later.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle regular text messages"""
        text = update.message.text.lower()
        if 'thank' in text:
            await update.message.reply_text("You're welcome! 😊")
        elif 'job' in text and 'find' in text:
            await update.message.reply_text("I'm actively searching for jobs. I'll notify you immediately when I find a good match!")
        else:
            await update.message.reply_text(
                "I'm your job search assistant. Use the commands to control your job search:\n"
                "/start - Begin job searching\n"
                "/stats - See application statistics\n"
                "/stop - Pause job searching\n"
                "/resume - Resume job searching"
            )
    
    async def notify_new_job(self, job_info):
        """Notify user about a new job found"""
        message = (
            f"🚨 *New Job Found!*\n\n"
            f"*Position:* {job_info['title']}\n"
            f"*Company:* {job_info['company']}\n"
            f"*Location:* {job_info.get('location', 'Remote')}\n\n"
            f"Should I apply? Reply 'yes' within 5 minutes to apply automatically."
        )
        # Send to all active chats
        for chat_id in self.get_active_chats():
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            )
    
    async def notify_application_sent(self, job_info, success=True):
        """Notify user about application status"""
        status = "✅ Successfully applied" if success else "❌ Failed to apply"
        message = (
            f"{status} for:\n"
            f"*{job_info['title']}* at {job_info['company']}\n"
            f"Location: {job_info.get('location', 'Remote')}"
        )
        for chat_id in self.get_active_chats():
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            )
    
    async def notify_job_offer(self, job_info):
        """Notify user about a job offer"""
        message = (
            f"🎉 *CONGRATULATIONS!*\n\n"
            f"You received a job offer from:\n"
            f"*{job_info['company']}* for {job_info['title']}\n\n"
            f"Job searching has been paused. Use /resume to continue searching."
        )
        for chat_id in self.get_active_chats():
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            )
    
    def get_active_chats(self):
        """Get all active chat IDs (simplified)"""
        # In production, store in database
        return [config.TELEGRAM_CHAT_ID]
    
    def run(self):
        """Run the bot"""
        self.application.run_polling()
    
    def get_main_keyboard(self):
        """Create custom keyboard (simplified)"""
        # Implementation would use ReplyKeyboardMarkup
        return None

# Singleton instance
telegram_bot = TelegramBot(config.TELEGRAM_TOKEN)
