import logging
import os
from dotenv import load_dotenv
from telegram import ForceReply ,Update ,ReplyKeyboardMarkup ,ReplyKeyboardRemove
from telegram.ext import Application , CommandHandler , ContextTypes , MessageHandler , filters ,ConversationHandler
import database
import jdatetime
import datetime
dbase=database.Database()

TYPE ,AMOUNT ,INCOME_DETAIL ,EXPENSE_DETAIL ,INVESTMENT_TYPE ,INVESTMENT_UNIT_AMOUNT ,INVESTMENT_CUSTOM_NAME ,DATE =range(8)

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
    
    
async def add_start(update:Update , context: ContextTypes.DEFAULT_TYPE)-> int:
    reply_keyboard=[["درآمد","خرج","سرمایه گذاری"]]
    await update.message.reply_text("چی میخوای اضافه کنی؟",
    reply_markup=ReplyKeyboardMarkup(reply_keyboard,one_time_keyboard=True,input_field_placeholder="چی میخوای اضافه کنی ؟",resize_keyboard=True))
    
    return TYPE

async def get_type(update:Update , context: ContextTypes.DEFAULT_TYPE)->int:
    
    user_type=update.message.text
    if user_type=="درآمد":
        context.user_data["type"]="income"
    elif user_type=="خرج":
        context.user_data["type"]="expense"
    elif user_type=="سرمایه گذاری":
        context.user_data["type"]="investment"
    else:
        await update.message.reply_text("لطفا یکی از گزینه ها رو انتخاب کنید ")
        return TYPE
    await update.message.reply_text("لطفا مقدارش رو به تومان وارد کن",reply_markup=ReplyKeyboardRemove())
    return AMOUNT

async def get_amount(update:Update , context: ContextTypes.DEFAULT_TYPE)->int:
    keyboard=[["رد شو"]]
    try:
        amount=float(update.message.text)
        context.user_data["amount"]=amount

    except ValueError:
        await update.message.reply_text("لطفا مقدار رو به عدد وارد کن")
        return AMOUNT
    
    if context.user_data["type"]=="income":
        await update.message.reply_text("منبع درآمدت رو بگو مثلا سود سهام,حقوق و... (اختیاری)",reply_markup=ReplyKeyboardMarkup(keyboard,one_time_keyboard=True,resize_keyboard=True))
        return INCOME_DETAIL
    
    elif context.user_data["type"]=="expense":
        await update.message.reply_text("دلیل خرج کردنت رو بگو؟(اختیاری)",reply_markup=ReplyKeyboardMarkup(keyboard,one_time_keyboard=True,resize_keyboard=True))
        return EXPENSE_DETAIL
    
    elif context.user_data["type"]=="investment":
        reply_keyboard=[["طلا","نقره","سکه"],["دلار","یورو","بیتکوین"],["سایر"]]
        await update.message.reply_text("نوع سرمایه گذاری رو انتخاب کن ",reply_markup=ReplyKeyboardMarkup(reply_keyboard,one_time_keyboard=True,input_field_placeholder="نوع سرمایه گذاری",resize_keyboard=True))
        return INVESTMENT_TYPE

async def get_description(update:Update , context: ContextTypes.DEFAULT_TYPE)->int:
    detail=update.message.text
    kyeboard=[["امروز","دیروز"]]
    if detail=="رد شو" :
        context.user_data["description"]=None
    else:
      context.user_data["description"]=detail
    
    await update.message.reply_text("تاریخ رو انتخاب کن یا با فرمت ۱۰-۰۴-۱۴۰۴ وارد کن ",reply_markup=ReplyKeyboardMarkup(kyeboard,one_time_keyboard=True,input_field_placeholder="انتخاب تاریخ",resize_keyboard=True))
    return DATE
             
async def get_income_detail(update:Update , context: ContextTypes.DEFAULT_TYPE)->int:
    return await get_description(update,context)

async def get_expense_detail(update:Update , context: ContextTypes.DEFAULT_TYPE)->int:
    return await get_description(update,context)

async def get_investment_type(update:Update , context: ContextTypes.DEFAULT_TYPE)->int:
    investment_type=update.message.text       
    if investment_type=="طلا":
        context.user_data["investment_type"]="gold"
    elif investment_type=="نقره":
        context.user_data["investment_type"]="silver"
    elif investment_type=="سکه" :
        context.user_data["investment_type"]="coin"
    elif investment_type=="دلار":
        context.user_data["investment_type"]="usd"
    elif investment_type=="یورو":
        context.user_data["investment_type"]="eur"
    elif investment_type=="بیتکوین":
        context.user_data["investment_type"]="bitcoin"
    elif investment_type=="سایر":
        context.user_data["investment_type"]="other"
    else:
        await update.message.reply_text("لطفاً یکی از گزینه‌ها رو انتخاب کن.")
        return INVESTMENT_TYPE
    if investment_type=="سایر":
        await update.message.reply_text("اسم سرمایه گذاری خاصت چیه ؟")
        return INVESTMENT_CUSTOM_NAME
        
    else:
        await update.message.reply_text("مقدار سرمایه گذاریت رو بدون واحدش بگو مثلا اگه ۱۰ دلار فقط بنویس ۱۰")
        return INVESTMENT_UNIT_AMOUNT

async def get_investment_unit_amount(update:Update , context: ContextTypes.DEFAULT_TYPE)->int:
    kyeboard=[["امروز","دیروز"]]
    
    try:
        unit_amount=float(update.message.text)
        context.user_data["investment_unit_amount"]=unit_amount
    except ValueError:
        await update.message.reply_text("لطفاً فقط عدد وارد کن.")
        return INVESTMENT_UNIT_AMOUNT
    
    await update.message.reply_text("تاریخ رو انتخاب کن یا با فرمت ۱۰-۰۴-۱۴۰۴ وارد کن ",reply_markup=ReplyKeyboardMarkup(kyeboard,one_time_keyboard=True,input_field_placeholder="انتخاب تاریخ",resize_keyboard=True))
    return DATE

async def get_investment_custom_name(update:Update , context: ContextTypes.DEFAULT_TYPE)->int:
    custom_name=update.message.text
    kyeboard=[["امروز","دیروز"]]
    context.user_data["investment_custom_name"]=custom_name
    await update.message.reply_text("تاریخ رو انتخاب کن یا با فرمت ۱۰-۰۴-۱۴۰۴ وارد کن ",reply_markup=ReplyKeyboardMarkup(kyeboard,one_time_keyboard=True,input_field_placeholder="انتخاب تاریخ",resize_keyboard=True))
    return DATE

async def save_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    users_id = dbase.fetch_query("SELECT id FROM users WHERE telegram_id=%s", (telegram_id,))

    try:
        transaction_id = dbase.execute_query(
            "INSERT INTO transactions(user_id, type, amount, description, date) VALUES(%s,%s,%s,%s,%s)",
            (users_id[0][0], context.user_data["type"], context.user_data["amount"],
             context.user_data.get("description"), context.user_data["date"])
        )

        if context.user_data["type"] == "investment":
            dbase.execute_query(
                "INSERT INTO investments(transactions_id, asset_type, unit_amount, custom_name) VALUES(%s,%s,%s,%s)",
                (transaction_id, context.user_data["investment_type"],
                 context.user_data.get("investment_unit_amount"),
                 context.user_data.get("investment_custom_name"))
            )

        await update.message.reply_text("ثبت شد ✅",reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
    except Exception as e:
        logger.error(f"Database error in save_transaction: {e}")
        await update.message.reply_text("مشکلی پیش اومد، دوباره امتحان کن.")

async def get_date(update:Update , context: ContextTypes.DEFAULT_TYPE)->int:
    
    date=update.message.text
    today=jdatetime.date.today()
    yesterday=today - jdatetime.timedelta(days=1)
    if date=="امروز":
        chosen_date=today
    elif date=="دیروز":
        chosen_date=yesterday
    else:
        try:
            chosen_date=jdatetime.datetime.strptime(date,"%Y-%m-%d").date()
        except ValueError:
            await update.message.reply_text("فرمتی که تاریخ رو باید بنویسی:۳-۰۵-۱۴۰۴")
            return DATE

    context.user_data["date"]=chosen_date.togregorian()
    await save_transaction(update,context)
    return ConversationHandler.END

async def cancel(update:Update , context: ContextTypes.DEFAULT_TYPE)->int:
    context.user_data.clear()
    await update.message.reply_text("لغو شد !",reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def set_new_period(update:Update , context: ContextTypes.DEFAULT_TYPE):
    user_id=update.effective_user.id
    date=datetime.datetime.now().date()
    try:
        
        dbase.execute_query("UPDATE users SET period_start_date=%s WHERE telegram_id=%s",(date,user_id))
        await update.message.reply_text("✅ با موفقیت دوره جدید مالی اغاز شد ")  
    except Exception as e:
        logger.error(f"Data base error in set new period :{e}")
        await update.message.reply_text("مشکلی پیش اومده مجدد تلاش کنیم")
 
async def report(update:Update , context: ContextTypes.DEFAULT_TYPE):
    user_id=update.effective_user.id
    
    try:
        user_id_period_time=dbase.fetch_query("select id , period_start_date from users where telegram_id=%s ",(user_id,))
        
    except Exception as e:
        logger.error(f"Error retrieving ID and periodic date from the database : {e}")
        await update.message.reply_text("مشکلی پیش اومد، دوباره امتحان کن.")
        return
    
    if user_id_period_time[0][1]==None :
        
        try:   
            sum_income=dbase.fetch_query("select sum(amount) as sum_income  from transactions where user_id= %s  and type= 'income' ",(user_id_period_time[0][0],))
            sum_expense=dbase.fetch_query("select sum(amount) as sum_expense  from transactions where user_id= %s  and type= 'expense' ",(user_id_period_time[0][0],))
        except Exception as e:
            logger.error(f"Error retrieving the sum of income and expenses from the database {e}")

        try:
            transactions=dbase.fetch_query("select type ,amount ,description ,date from transactions where user_id= %s and type in ('expense','income') order by type ",(user_id_period_time[0][0],))
        except Exception as e:
            logger.error(f"get transactions : {e}")
    
    
    else:
        try:   
            sum_income=dbase.fetch_query("select sum(amount) as sum_income  from transactions where user_id= %s and %s<= date and type= 'income' ",(user_id_period_time[0][0],user_id_period_time[0][1]))
            sum_expense=dbase.fetch_query("select sum(amount) as sum_expense  from transactions where user_id= %s and %s<= date and type= 'expense' ",(user_id_period_time[0][0],user_id_period_time[0][1]))
        except Exception as e:
            logger.error(f"Error retrieving the sum of income and expenses from the database {e}")

        try:
            transactions=dbase.fetch_query("select type ,amount ,description ,date from transactions where user_id= %s and %s<= date and type in ('expense','income') order by type ",(user_id_period_time[0][0],user_id_period_time[0][1]))
        except Exception as e:
            logger.error(f"get transactions : {e}")
    
    income_value=sum_income[0][0] or 0
    expense_value=sum_expense[0][0] or 0
    
    balance=income_value-expense_value

    summary=(
        f"📊 گزارش مالی دوره جاری\n\n"
        f"💰 جمع درآمدها: {income_value:,.0f} تومان\n"
        f"💸 جمع مخارج:   {expense_value:,.0f} تومان\n"
        f"⚖️ مانده حساب: {balance:,.0f} تومان\n"
    )
    row_transactios=[]
    
    for row in transactions:
        t_type ,t_amount ,t_desc ,t_date =row
        
        j_date=jdatetime.date.fromgregorian(date=t_date)
        date_str=f"{j_date.year}/{str(j_date.month).zfill(2)}/{str(j_date.day).zfill(2)}"
    
        if t_type=="income":
            lines=f"📥 درآمد --> {t_desc or "بدون توضیح"} : {t_amount:,.0f}تومان  {date_str}"
            row_transactios.append(lines)
        elif t_type=="expense":
            lines=f"📤 خرج  --> {t_desc or "بدون توضیح"} : {t_amount:,.0f}تومان  {date_str}"
            row_transactios.append(lines)
     
    if not row_transactios:
        await update.message.reply_text("هنوز در این دوره مالی تراکنشی ثبت نکرده اید")
        return
    
    report_text = summary + "──────────────\n\n" + "\n\n".join(row_transactios)
    await update.message.reply_text(report_text)
     
async def help_command(update:Update , context: ContextTypes.DEFAULT_TYPE) -> None :
    await update.message.reply_text("helppppp!")
    
    await update.message.reply_text(update.message.text)
    
    
def main():
    application=Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("set_new_period", set_new_period))
    application.add_handler(CommandHandler("report",report))
    conv_handler=ConversationHandler(
        entry_points=[CommandHandler("addtransaction",add_start)],
        states={TYPE:[MessageHandler(filters.TEXT & ~filters.COMMAND ,get_type)],
            AMOUNT:[MessageHandler(filters.TEXT & ~filters.COMMAND,get_amount)],
            INCOME_DETAIL:[MessageHandler(filters.TEXT & ~filters.COMMAND,get_income_detail)],
            EXPENSE_DETAIL:[MessageHandler(filters.TEXT & ~filters.COMMAND,get_expense_detail)],
            INVESTMENT_TYPE:[MessageHandler(filters.TEXT & ~filters.COMMAND,get_investment_type)],
            INVESTMENT_UNIT_AMOUNT:[MessageHandler(filters.TEXT & ~filters.COMMAND,get_investment_unit_amount)],
            INVESTMENT_CUSTOM_NAME:[MessageHandler(filters.TEXT & ~filters.COMMAND,get_investment_custom_name)],
            DATE:[MessageHandler(filters.TEXT & ~filters.COMMAND,get_date)]},
        
        fallbacks=[CommandHandler("cancel", cancel)])

    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    
if __name__ == "__main__":
        main()