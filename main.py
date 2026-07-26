import logging
import os
from dotenv import load_dotenv
from telegram import ForceReply , Update
from telegram.ext import Application , CommandHandler , ContextTypes , MessageHandler , filters
import database

dbase=database.Database()

load_dotenv()
TOKEN=os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger= logging.getLogger(__name__)

async def start(update:Update, context:ContextTypes.DEFAULT_TYPE)-> None:
    
    user=update.effective_user
    
    try:
        id=user.id
        user_name=user.username
        have_user=dbase.fetch_query("SELECT telegram_id FROM users WHERE telegram_id=%s ",(id,))
        
        if not have_user :
            dbase.execute_query("INSERT INTO users(telegram_id, username) VALUES(%s,%s)",(id,user_name))
    except Exception as e:
        logger.error(f"Database error in start handler : {e}")
        
    
    await update.message.reply_html(
        rf"hi {user.mention_html()}" ,
        reply_markup=ForceReply(selective=True)
    )
    
    
async def help_command(update:Update , context: ContextTypes.DEFAULT_TYPE) -> None :
    await update.message.reply_text("helppppp!")
    
async def echo(update:Update , context : ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)
    
    
def main():
    application=Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND , echo))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    
if __name__ == "__main__":
        main()