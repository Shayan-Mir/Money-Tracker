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
REMOVE_TYPE ,GET_ENUM ,REMOVE_CONFIRM =range(3)

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
        
    welcome = (
        f"سلام {user.first_name}! 👋\n\n"
        "🏦 <b>به MoneyTracker 💵 خوش اومدی!</b>\n\n"
        "این بات کمکت می‌کنه پولت رو بهتر مدیریت کنی:\n\n"
        "📥 درآمدهات رو ثبت کن\n"
        "📤 خرج‌هات رو ثبت کن\n"
        "💰 سرمایه‌گذاری‌هات رو پیگیری کن\n"
        "📊 گزارش مالی بگیر\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🚀 <b>برای شروع:</b>\n"
        "اول با دستور /addtransaction یه تراکنش ثبت کن!\n\n"
        "❓ هر سؤالی داری، دستور /help رو بزن."
    )

    await update.message.reply_text(welcome, parse_mode="HTML")
    
    
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
        await update.message.reply_text("⚠️ لطفاً یکی از دکمه‌های زیر رو انتخاب کن")
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
        await update.message.reply_text("📝 منبع درآمدت چیه؟ مثلاً: حقوق، سود سهام و...\n\nیا دکمه «رد شو» رو بزن",reply_markup=ReplyKeyboardMarkup(keyboard,one_time_keyboard=True,resize_keyboard=True))
        return INCOME_DETAIL
    
    elif context.user_data["type"]=="expense":
        await update.message.reply_text("📝 بابت چی خرج کردی؟ مثلاً: اجاره، خرید و...\n\nیا دکمه «رد شو» رو بزن",reply_markup=ReplyKeyboardMarkup(keyboard,one_time_keyboard=True,resize_keyboard=True))
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
        await update.message.reply_text("💎 اسم سرمایه‌گذاریت رو بنویس:")
        return INVESTMENT_CUSTOM_NAME
        
    else:
        await update.message.reply_text("🔢 مقدار سرمایه‌گذاری رو وارد کن (بدون واحد)\n\nمثلاً: ۱۰")
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
    today=jdatetime.datetime.now()
    yesterday=today - jdatetime.timedelta(days=1)
    if date=="امروز":
        chosen_date=today
    elif date=="دیروز":
        chosen_date=yesterday
    else:
        try:
            chosen_date=jdatetime.datetime.strptime(date,"%Y-%m-%d")
            if chosen_date.date() == jdatetime.date.today():
                chosen_date = jdatetime.datetime.now()
        except ValueError:
            await update.message.reply_text("⚠️ فرمت تاریخ اشتباهه!\n\nفرمت صحیح: ۱۴۰۴-۰۵-۰۳")
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
    date=datetime.datetime.now()
    try:
        
        dbase.execute_query("UPDATE users SET period_start_date=%s WHERE telegram_id=%s",(date,user_id))
        await update.message.reply_text("✅ دوره مالی جدید با موفقیت شروع شد!")  
    except Exception as e:
        logger.error(f"Data base error in set new period :{e}")
        await update.message.reply_text("❌ مشکلی پیش اومد، لطفاً دوباره امتحان کن")
        return
async def report(update:Update , context: ContextTypes.DEFAULT_TYPE):
    user_id=update.effective_user.id
    
    try:
        user_id_period_time=dbase.fetch_query("select id , period_start_date from users where telegram_id=%s ",(user_id,))

        if not user_id_period_time:
            await update.message.reply_text("❌ حساب کاربری پیدا نشد.\n\nاول دستور /start رو بزن")
            return
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
            return
        try:
            transactions=dbase.fetch_query("select type ,amount ,description ,date from transactions where user_id= %s and type in ('expense','income') order by type ",(user_id_period_time[0][0],))
        except Exception as e:
            logger.error(f"get transactions : {e}")
            return
    
    else:
        try:   
            sum_income=dbase.fetch_query("select sum(amount) as sum_income  from transactions where user_id= %s and %s<= date and type= 'income' ",(user_id_period_time[0][0],user_id_period_time[0][1]))
            sum_expense=dbase.fetch_query("select sum(amount) as sum_expense  from transactions where user_id= %s and %s<= date and type= 'expense' ",(user_id_period_time[0][0],user_id_period_time[0][1]))
        except Exception as e:
            logger.error(f"Error retrieving the sum of income and expenses from the database {e}")
            return
        try:
            transactions=dbase.fetch_query("select type ,amount ,description ,date from transactions where user_id= %s and %s<= date and type in ('expense','income') order by type ",(user_id_period_time[0][0],user_id_period_time[0][1]))
        except Exception as e:
            logger.error(f"get transactions : {e}")
            return
    income_value=sum_income[0][0] or 0
    expense_value=sum_expense[0][0] or 0
    
    balance=income_value-expense_value

    summary=(
        f"📊 گزارش مالی دوره جاری\n\n"
        f"💰 جمع درآمدها: {income_value:,.0f} تومان\n"
        f"💸 جمع مخارج:   {expense_value:,.0f} تومان\n"
        f"⚖️ مانده حساب: {balance:,.0f} تومان\n"
    )
    row_transactions=[]
    
    for row in transactions:
        t_type ,t_amount ,t_desc ,t_date =row
        
        j_date=jdatetime.date.fromgregorian(date=t_date)
        date_str=f"{j_date.year}/{str(j_date.month).zfill(2)}/{str(j_date.day).zfill(2)}"
    
        if t_type=="income":
            lines=f"📥 درآمد --> {t_desc or 'بدون توضیح'} : {t_amount:,.0f}تومان  {date_str}"
            row_transactions.append(lines)
        elif t_type=="expense":
            lines=f"📤 خرج  --> {t_desc or 'بدون توضیح'} : {t_amount:,.0f}تومان  {date_str}"
            row_transactions.append(lines)
     
    if not row_transactions:
        await update.message.reply_text("📭 در این دوره مالی هنوز تراکنشی ثبت نکردی!")
        return

    report_text = summary + "──────────────\n\n" + "\n\n".join(row_transactions)
    await update.message.reply_text(report_text)

async def investments(update:Update , context: ContextTypes.DEFAULT_TYPE):
    user_id=update.effective_user.id
    
    try:
        user_id_db=dbase.fetch_query("select id from users where telegram_id=%s ",(user_id,))

        if not user_id_db:
            await update.message.reply_text("❌ حساب کاربری پیدا نشد.\n\nاول دستور /start رو بزن")
            return
    except Exception as e:
        logger.error(f"Error retrieving ID and periodic date from the database : {e}")
        await update.message.reply_text("مشکلی پیش اومد، دوباره امتحان کن.")
        return

    try:
        investments=dbase.fetch_query("""SELECT t.amount ,t.date ,i.asset_type ,i.custom_name ,
                        i.unit_amount from transactions t 
                        INNER join investments i 
                        ON t.id=i.transactions_id
                        WHERE t.user_id=%s
                        ORDER by i.asset_type,t.date ;""",(user_id_db[0][0],))
    except Exception as e:
        logger.error(f"Error retrieving investments date from the database : {e}")
        return
    
    row_investments=[]

    sum_investments={"gold":[0] ,"silver":[0] ,"coin":[0] ,"usd":[0] ,"eur":[0] ,"bitcoin":[0]}
    
    for row in investments:
        t_amount ,t_date ,i_asset_type ,i_custom_name ,i_unit_amount=row
        jalai_date=jdatetime.date.fromgregorian(date=t_date)
        str_date=f"{jalai_date.year}/{str(jalai_date.month).zfill(2)}/{str(jalai_date.day).zfill(2)}"

        if i_asset_type!="other":
                if i_asset_type =="gold":
                    sum_investments["gold"][0]+=i_unit_amount
                    emoji="🥇"
                    asset_type="طلا"
                    Unit="گرم"
                elif i_asset_type =="silver":
                    sum_investments["silver"][0]+=i_unit_amount
                    emoji="🥈"
                    asset_type="نقره"
                    Unit="گرم"
                elif i_asset_type =="coin" :
                    sum_investments["coin" ][0]+=i_unit_amount
                    emoji="🪙"
                    asset_type="سکه"
                    Unit="سکه"
                elif i_asset_type =="usd":
                    sum_investments["usd"][0]+=i_unit_amount
                    emoji="💵"
                    asset_type="دلار"
                    Unit="دلار"
                elif i_asset_type =="eur":
                    sum_investments["eur"][0]+=i_unit_amount
                    emoji="💶"
                    asset_type="یورو"
                    Unit="یورو"
                elif i_asset_type =="bitcoin":
                    sum_investments["bitcoin"][0]+=i_unit_amount
                    emoji="🔶"
                    asset_type="بیتکوین"
                    Unit="بیتکوین"
                    
                lines=f"{emoji}{asset_type} ---> {t_amount:,.0f}تومان ---> {i_unit_amount} {Unit} ---> {str_date}"
                row_investments.append(lines)        
        else:
            emoji="💎"
            lines=f"{emoji}{i_custom_name} ---> {t_amount:,.0f}تومان --->{str_date}"
            row_investments.append(lines)
    
    summary=[]
    
    if sum_investments["gold"]!=[0]:
        summary.append(f"طلا :{sum_investments['gold'][0]} گرم 🥇 \n\n")
    
    if sum_investments["silver"]!=[0] :
        summary.append(f"مقدار کل نقره :{sum_investments['silver'][0]} گرم 🥈\n\n")    
     
    if sum_investments["coin"]!=[0] :
        summary.append(f"مقدار کل سکه‌ :{sum_investments['coin'][0]} عدد 🪙\n\n")
    
    if sum_investments["usd"]!=[0]:
        summary.append(f"مقدار کل دلار :{sum_investments['usd'][0]} دلار 💵\n\n")
        
    if sum_investments["eur"]!=[0]:
        summary.append(f"مقدار کل یورو :{sum_investments['eur'][0]} یورو 💶 \n\n")
    
    if sum_investments["bitcoin"]!=[0]:
        summary.append(f"مقدار کل بیتکوین :{sum_investments['bitcoin'][0]} بیتکوین 🔶 \n\n")
    
        
    # summary=(f"مقدار کل طلا :{sum_investments["gold"][0]} گرم  به ارزش {sum_investments["gold"][1]:,.0f} تومان\n\n")
    if not row_investments:
        await update.message.reply_text("هنوز هیچ سرمایه‌گذاری ثبت نکردی.")
    else:
        report_text ="🏅 **خلاصه وضعیت سرمایه‌گذاری‌ها** :\n\n"+"".join(summary) + "──────────────\n\n" +"جزئیات سرمایه گذاری ها: \n\n"+"\n\n".join(row_investments)
        await update.message.reply_text(report_text)

async def show_all_transactions(update:Update , context: ContextTypes.DEFAULT_TYPE):
    user_id=update.effective_user.id
    try:
        user_id_db=dbase.fetch_query("select id from users where telegram_id=%s ",(user_id,))
        
    except Exception as e:
        logger.error(f"Error retrieving ID and periodic date from the database : {e}")
        await update.message.reply_text("مشکلی پیش اومد، دوباره امتحان کن.")
        return
    
    try:
        transactios=dbase.fetch_query("SELECT type , amount, description ,date FROM transactions WHERE user_id=%s and type in('income' ,'expense' ) ORDER by type",(user_id_db[0][0],))
    except Exception as e:
        logger.error(f"Error retrieving transactions from database{e}")
        await update.message.reply_text("مشکلی پیش اومد، دوباره امتحان کن.")
        return
    row_transactions=[]
    for row in transactios:
        t_type ,t_amount ,t_desc ,t_date =row
        jalai_date=jdatetime.datetime.fromgregorian(date=t_date)
        str_date=f"{jalai_date.year}/{str(jalai_date.month).zfill(2)}/{str(jalai_date.day).zfill(2)}"
        
        if t_type=="income":
            lines=f"📥 درآمد --> {t_desc or 'بدون توضیح'} : {t_amount:,.0f}تومان  {str_date}"
            row_transactions.append(lines)
        elif t_type=="expense":
            lines=f"📤 خرج  --> {t_desc or 'بدون توضیح'} : {t_amount:,.0f}تومان  {str_date}"
            row_transactions.append(lines)
            
    if not row_transactions:
        await update.message.reply_text("📭 هنوز تراکنشی ثبت نکردی!")
        return
    await update.message.reply_text("📋 تمام تراکنش‌های درآمد و خرج:\n\n" +"──────────────\n\n"+ "\n\n".join(row_transactions))

async def remove(update:Update , context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard=[["درآمد/خرج","سرمایه گذاری"]]
    await update.message.reply_text("🗑️ چه نوع تراکنشی رو می‌خوای حذف کنی؟",reply_markup=ReplyKeyboardMarkup(reply_keyboard,one_time_keyboard=True,input_field_placeholder="چه تراکنشی قرار پاک بشه",resize_keyboard=True))
    
    return REMOVE_TYPE

async def get_db_user_id(update:Update , context: ContextTypes.DEFAULT_TYPE):
    user_id=update.effective_user.id
    try:
        user_id_db=dbase.fetch_query("select id from users where telegram_id=%s ",(user_id,))
        return user_id_db
    except Exception as e:
        logger.error(f"Error retrieving ID and periodic date from the database : {e}")
        await update.message.reply_text("مشکلی پیش اومد، دوباره امتحان کن.")
        return
    
def change_jdate(t_date):
        jalai_date=jdatetime.datetime.fromgregorian(date=t_date)
        str_date=f"{jalai_date.year}/{str(jalai_date.month).zfill(2)}/{str(jalai_date.day).zfill(2)}"
        return str_date

async def get_remove_type(update:Update , context: ContextTypes.DEFAULT_TYPE):
    remove_type=update.message.text
    context.user_data["remove_type"]=remove_type
    
    if remove_type=="درآمد/خرج":
        return await show_income_expense_list(update,context)
    
    elif remove_type=="سرمایه گذاری":
        return await show_investments_list(update,context)
    
    else :
        await update.message.reply_text("⚠️ لطفاً یکی از دکمه‌های زیر رو انتخاب کن")
        return REMOVE_TYPE
    
    
    
async def show_income_expense_list(update:Update , context: ContextTypes.DEFAULT_TYPE):
        
        user_id_db=await get_db_user_id(update,context)
        if not user_id_db:       
            return ConversationHandler.END
        
        try:
            income_expense_list=dbase.fetch_query("SELECT id, type , amount, description ,date FROM transactions WHERE user_id=%s and type in ('income','expense') ORDER by type ",(user_id_db[0][0],))
        except Exception as e:
            logger.error(f"Error retrieving income and expenses from the database in the `show_income_expense_list` function{e}")
            await update.message.reply_text("مشکلی پیش اومد، دوباره امتحان کن.")
            return ConversationHandler.END

        enum_data=enumerate(income_expense_list,start=1)
        row_transactions=[]
        mapping = {}
        for row in enum_data:
            enum=row[0]
            t_id ,t_type ,t_amount ,t_desc ,t_date =row[1]
            str_date=change_jdate(t_date)
            mapping[enum]=t_id
            if t_type=="income":
                lines=f"{enum}_ درآمد --> {t_desc or 'بدون توضیح'} : {t_amount:,.0f}تومان  {str_date}"
                row_transactions.append(lines)
            elif t_type=="expense":
                lines=f"{enum}_ خرج  --> {t_desc or 'بدون توضیح'} : {t_amount:,.0f}تومان  {str_date}"
                row_transactions.append(lines)
        context.user_data["remove_map"]=mapping
        context.user_data["transactions"]=row_transactions
        context.user_data["remove_type"]="income_expense"
        
        if not row_transactions:
            await update.message.reply_text("📭 هنوز تراکنش درآمد/خرجی ثبت نکردی!")
            return ConversationHandler.END
       
        await update.message.reply_text("🔢 شماره تراکنشی که میخوای حذف کنی رو وارد کن:\n\n"+"\n\n".join(row_transactions),reply_markup=ReplyKeyboardRemove())
       
        return GET_ENUM

    
async def show_investments_list(update:Update , context: ContextTypes.DEFAULT_TYPE):
    user_id_db=await get_db_user_id(update,context)
    if not user_id_db:       
        return ConversationHandler.END
    try:
        investments_list=dbase.fetch_query("""SELECT t.id, t.amount ,t.date ,i.asset_type ,i.custom_name ,
                        i.unit_amount from transactions t 
                        INNER join investments i 
                        ON t.id=i.transactions_id
                        WHERE t.user_id=%s
                        ORDER by i.asset_type,t.date""",(user_id_db[0][0],))
    except Exception as e:
        logger.error(f"Error retrieving investments from the database in the `show_investments_list` function{e}")
        await update.message.reply_text("مشکلی پیش اومد، دوباره امتحان کن.")
        return ConversationHandler.END
    
    asset_type={
    "gold": "طلا",
    "silver": "نقره",
    "coin": "سکه",
    "usd": "دلار",
    "eur": "یورو",
    "bitcoin": "بیتکوین",
    "other": "سایر"
}   
    
    enum_date=enumerate(investments_list,start=1)
    row_transactions=[]
    mapping={}
    for row in enum_date:
        enum=row[0]
        t_id, t_amount ,t_date ,i_asset_type ,i_custom_name , i_unit_amount=row[1]
        mapping[enum]=t_id
        str_date=change_jdate(t_date)
        investment_type=asset_type[i_asset_type]
        
        if investment_type=="سایر":
            lines=f"{enum}_ {i_custom_name} ---> {t_amount:,.0f}تومان --->{str_date}"
            row_transactions.append(lines)
        
        elif investment_type in ("طلا","نقره"):
            lines=f"{enum}_ {investment_type} ---> {t_amount:,.0f}تومان ---> {i_unit_amount} گرم ---> {str_date}"
            row_transactions.append(lines)  
        
        else:
            lines=f"{enum}_ {investment_type} ---> {t_amount:,.0f}تومان ---> {i_unit_amount} {investment_type} ---> {str_date}"
            row_transactions.append(lines)

    context.user_data["remove_map"]=mapping
    context.user_data["transactions"]=row_transactions
    context.user_data["remove_type"]="investments"
    
    if not row_transactions:
        await update.message.reply_text("📭 هنوز سرمایه‌گذاری ثبت نکردی!")
        return ConversationHandler.END
    
    await update.message.reply_text("🔢 شماره تراکنشی که میخوای حذف کنی رو وارد کن:\n\n"+"\n\n".join(row_transactions),reply_markup=ReplyKeyboardRemove())
    
    return GET_ENUM

async def get_enum(update:Update , context: ContextTypes.DEFAULT_TYPE):
    try:
        get_e_num=int(update.message.text)        
    except ValueError:
        await update.message.reply_text("⚠️ لطفاً فقط عدد وارد کن")
        return GET_ENUM
    try:
        real_id=context.user_data["remove_map"][get_e_num]
    except KeyError:
        await update.message.reply_text("⚠️ این عدد توی لیست نیست!\n\nیکی از اعداد لیست رو وارد کن")
        return GET_ENUM
    
    
    context.user_data["remove_id"]=real_id
    transaction=context.user_data["transactions"][get_e_num-1]
    keyboard=[["بله ✅","خیر ❌"]]
    await update.message.reply_text(f"⚠️ آیا مطمئنی می‌خوای این تراکنش رو حذف کنی؟\n\n{transaction}",reply_markup=ReplyKeyboardMarkup(keyboard,one_time_keyboard=True,resize_keyboard=True,input_field_placeholder="پاکش کنیم یا نه!؟"))
    
    return REMOVE_CONFIRM


        
async def set_remove_choose(update:Update , context: ContextTypes.DEFAULT_TYPE):
    fainal_check=update.message.text
    user_id_db=await get_db_user_id(update,context)
    
    if not user_id_db:       
        return ConversationHandler.END
    
    if fainal_check=="بله ✅":
        id=context.user_data["remove_id"]
        if context.user_data["remove_type"]=="investments":
            try:
                check = dbase.fetch_query(
                    "SELECT id FROM transactions WHERE id=%s AND user_id=%s", 
                    (id, user_id_db[0][0])
                )
                if not check:
                    await update.message.reply_text("❌ این تراکنش مال شما نیست!")
                    return ConversationHandler.END
                
                dbase.execute_query("DELETE from investments WHERE transactions_id=%s",(id,))
                dbase.execute_query("DELETE FROM transactions WHERE id=%s and user_id=%s",(id,user_id_db[0][0]))
            except Exception as e:
                logger.error(f"Error deleting an investment-type transaction in the set_remove_choose function:{e}")
                await update.message.reply_text("مشکلی پیش اومد، دوباره امتحان کن.",reply_markup= ReplyKeyboardRemove())
                return ConversationHandler.END
        elif context.user_data["remove_type"]=="income_expense":
            try:
                dbase.execute_query("DELETE FROM transactions WHERE id=%s AND user_id=%s",(id,user_id_db[0][0]))    
            except Exception as e:
                logger.error(f"Error when deleting an income/expense transaction in the `set_remove_choose` function:{e}")
                await update.message.reply_text("مشکلی پیش اومد، دوباره امتحان کن.",reply_markup= ReplyKeyboardRemove())
                return ConversationHandler.END
        await update.message.reply_text("با موفقیت حذف شد ✅",reply_markup= ReplyKeyboardRemove())
    elif fainal_check=="خیر ❌":
        await cancel(update,context)
    else:
        await update.message.reply_text("⚠️ لطفاً «بله ✅» یا «خیر ❌» رو انتخاب کن")
        return REMOVE_CONFIRM
    
    
    return ConversationHandler.END

    
async def help_command(update:Update , context: ContextTypes.DEFAULT_TYPE) -> None :
    await update.message.reply_text("🏦 راهنمای بات MoneyTracker 💵\n\n"
        "به بات خوش اومدی! 👋\n"
        "این بات بهت کمک می‌کنه درآمدها، خرج‌ها و سرمایه‌گذاری‌هات رو مدیریت کنی.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📋 **لیست کامندها:**\n\n"
        "🟢 /start — شروع و ثبت‌نام در بات\n"
        "➕ /addtransaction — اضافه کردن تراکنش جدید\n"
        "    ↳ می‌تونی درآمد، خرج یا سرمایه‌گذاری ثبت کنی\n"
        "    ↳ از کامند /cancel هم می‌تونی وسط کار لغو کنی\n\n"
        "📊 /report — گزارش مالی دوره جاری\n"
        "    ↳ جمع درآمدها، جمع خرج‌ها و مانده حساب رو نشون میده\n\n"
        "💰 /show_investments — نمایش سرمایه‌گذاری‌ها\n"
        "    ↳ خلاصه و جزئیات تمام سرمایه‌گذاری‌های ثبت‌شده\n\n"
        "📋 /transactions — لیست تمام تراکنش‌ها\n"
        "    ↳ تمام درآمدها و خرج‌های ثبت‌شده بدون فیلتر زمانی\n\n"
        "🔄 /set_new_period — شروع دوره مالی جدید\n"
        "    ↳ از این لحظه به بعد تراکنش‌های جدید رو پیگیری می‌کنه\n\n"
        "🗑️ /remove — حذف یک تراکنش\n"
        "    ↳ لیست تراکنش‌ها رو می‌بینی و عدد مورد نظر رو حذف می‌کنی\n\n"
        "❌ /cancel — لغو عملیات جاری\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "💡 **نکته:**\n"
        "هر ماه یا هر دوره‌ای که دوست داری، با /set_new_period شروع کن\n"
        "تا تراکنش‌های جدیدت رو جداگانه پیگیری کنی.\n\n"
        "برای شروع، دستور /start رو بزن! 🚀"
 )
   
   

    
def main():

    async def post_init(application):
        await application.bot.set_my_commands([
            ("start","شروع"),
            ("addtransaction","اضافه کردن یه تراکنش"),
            ("report","گزارش تراکنش ها "),
            ("show_investments","گزارش سرمایه گذاری ها "),
            ("show_all_transactions","نمایش تمام تراکنش ها"),
            ("set_new_period","شروع یه دوره مالی جدید"),
            ("help","راهنما"),
            ("remove","پاک کردن یک تراکنش"),
            ("cancel","لغو تراکنش")
        ])
    application=Application.builder().token(TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("set_new_period", set_new_period))
    application.add_handler(CommandHandler("report",report))
    application.add_handler(CommandHandler("show_investments",investments))
    application.add_handler(CommandHandler("show_all_transactions",show_all_transactions))
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

    conv_handler_remove_commend=ConversationHandler(
       entry_points=[CommandHandler("remove",remove)] ,
      
       states={REMOVE_TYPE:[MessageHandler(filters.TEXT & ~filters.COMMAND,get_remove_type)],
            #    SHOW_INCOME_EXPENSE:[MessageHandler(filters.TEXT & ~filters.COMMAND,show_income_expense_list)],
            #    SHOW_INVESTMENT:[MessageHandler(filters.TEXT & ~filters.COMMAND,show_investments_list)],
               GET_ENUM:[MessageHandler(filters.TEXT & ~filters.COMMAND,get_enum)],
               REMOVE_CONFIRM:[MessageHandler(filters.TEXT & ~filters.COMMAND,set_remove_choose)]      
       },
        fallbacks=[CommandHandler("cancel",cancel)]
    )
    
    application.add_handler(conv_handler)
    application.add_handler(conv_handler_remove_commend)
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    
if __name__ == "__main__":
        main()