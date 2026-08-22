# Money Tracker - ربات مدیریت مالی تلگرام

<div dir="rtl">

## 🇮🇷 نسخه فارسی

یک ربات تلگرامی برای مدیریت مالی شخصی با قابلیت ثبت درآمد، خرج و سرمایه‌گذاری.

### ✨ امکانات

- 📥 ثبت درآمدها با توضیحات دلخواه
- 📤 ثبت خرج‌ها با توضیحات دلخواه
- 💰 ثبت سرمایه‌گذاری‌ها (طلا، نقره، سکه، دلار، یورو، بیتکوین و سایر)
- 📊 گزارش مالی دوره جاری با جمع درآمدها و خرج‌ها
- 💹 نمایش سرمایه‌گذاری‌ها با جزئیات و خلاصه وضعیت
- 📋 لیست تمام تراکنش‌ها
- 🗑️ حذف تراکنش‌ها
- 🔄 مدیریت دوره مالی
- 📅 پشتیبانی از تقویم شمسی

### 🚀 دستورات ربات

| دستور | توضیح |
|:------|:------|
| `/start` | شروع و ثبت‌نام در بات |
| `/addtransaction` | اضافه کردن تراکنش جدید (درآمد/خرج/سرمایه‌گذاری) |
| `/report` | گزارش مالی دوره جاری |
| `/show_investments` | نمایش سرمایه‌گذاری‌ها |
| `/transactions` | لیست تمام تراکنش‌ها |
| `/set_new_period` | شروع دوره مالی جدید |
| `/remove` | حذف یک تراکنش |
| `/cancel` | لغو عملیات جاری |
| `/help` | راهنمای بات |

### 🛠️ نصب و راه‌اندازی

#### پیش‌نیازها

- Python 3.10+
- MySQL
- توکن ربات تلگرام (از @BotFather)

#### مراحل نصب

1. **کلون کردن پروژه:**
   ```bash
   git clone https://github.com/your-username/money-tracker.git
   cd money-tracker
   ```

2. **نصب وابستگی‌ها:**
   ```bash
   pip install python-telegram-bot mysql-connector-python jdatetime python-dotenv
   ```

4. **ایجاد فایل `.env`:**
   ```env
   TELEGRAM_TOKEN=your_bot_token_here
   MYSQL_ROOT_PASSWORD=your_password
   MYSQL_DATABASE=your_database_name
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   ```

5. **ایجاد جداول دیتابیس:**
   ```sql
   CREATE TABLE users (
       id INT AUTO_INCREMENT PRIMARY KEY,
       telegram_id BIGINT UNIQUE NOT NULL,
       username VARCHAR(255),
       period_start_date DATETIME
   );

   CREATE TABLE transactions (
       id INT AUTO_INCREMENT PRIMARY KEY,
       user_id INT NOT NULL,
       type ENUM('income', 'expense', 'investment') NOT NULL,
       amount DECIMAL(15, 2) NOT NULL,
       description TEXT,
       date DATETIME NOT NULL,
       FOREIGN KEY (user_id) REFERENCES users(id)
   );

   CREATE TABLE investments (
       id INT AUTO_INCREMENT PRIMARY KEY,
       transactions_id INT NOT NULL,
       asset_type ENUM('gold', 'silver', 'coin', 'usd', 'eur', 'bitcoin', 'other') NOT NULL,
       unit_amount DECIMAL(15, 4),
       custom_name VARCHAR(255),
       FOREIGN KEY (transactions_id) REFERENCES transactions(id)
   );
   ```

6. **اجرا کردن ربات:**
   ```bash
   python main.py
   ```

### 📁 ساختار پروژه

```
money-tracker/
├── main.py           # فایل اصلی ربات
├── database.py       # کلاس اتصال به دیتابیس
├── .env              # متغیرهای محیطی (git ignore شده)
├── .gitignore        # فایل‌های نادیده گرفته شده توسط git
└── README.md         # این فایل
```

### 📝 مجوز

این پروژه تحت مجوز MIT است.

---

</div>

# Money Tracker - Telegram Finance Bot

<div dir="ltr">

## 🇬🇧 English Version

A Telegram bot for personal finance management with income, expense, and investment tracking.

### ✨ Features

- 📥 Record income with custom descriptions
- 📤 Record expenses with custom descriptions
- 💰 Track investments (Gold, Silver, Coin, USD, EUR, Bitcoin, and more)
- 📊 Financial reports with income/expense summaries
- 💹 Investment portfolio view with details and summaries
- 📋 Complete transaction history
- 🗑️ Delete transactions
- 🔄 Financial period management
- 📅 Persian calendar (Jalali) support

### 🚀 Bot Commands

| Command | Description |
|:--------|:------------|
| `/start` | Start and register with the bot |
| `/addtransaction` | Add new transaction (income/expense/investment) |
| `/report` | Current period financial report |
| `/show_investments` | View investments |
| `/transactions` | List all transactions |
| `/set_new_period` | Start new financial period |
| `/remove` | Delete a transaction |
| `/cancel` | Cancel current operation |
| `/help` | Bot help guide |

### 🛠️ Installation & Setup

#### Prerequisites

- Python 3.10+
- MySQL
- Telegram bot token (from @BotFather)

#### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/money-tracker.git
   cd money-tracker
   ```

2. **Install dependencies:**
   ```bash
   pip install python-telegram-bot mysql-connector-python jdatetime python-dotenv
   ```

4. **Create `.env` file:**
   ```env
   TELEGRAM_TOKEN=your_bot_token_here
   MYSQL_ROOT_PASSWORD=your_password
   MYSQL_DATABASE=your_database_name
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   ```

5. **Create database tables:**
   ```sql
   CREATE TABLE users (
       id INT AUTO_INCREMENT PRIMARY KEY,
       telegram_id BIGINT UNIQUE NOT NULL,
       username VARCHAR(255),
       period_start_date DATETIME
   );

   CREATE TABLE transactions (
       id INT AUTO_INCREMENT PRIMARY KEY,
       user_id INT NOT NULL,
       type ENUM('income', 'expense', 'investment') NOT NULL,
       amount DECIMAL(15, 2) NOT NULL,
       description TEXT,
       date DATETIME NOT NULL,
       FOREIGN KEY (user_id) REFERENCES users(id)
   );

   CREATE TABLE investments (
       id INT AUTO_INCREMENT PRIMARY KEY,
       transactions_id INT NOT NULL,
       asset_type ENUM('gold', 'silver', 'coin', 'usd', 'eur', 'bitcoin', 'other') NOT NULL,
       unit_amount DECIMAL(15, 4),
       custom_name VARCHAR(255),
       FOREIGN KEY (transactions_id) REFERENCES transactions(id)
   );
   ```

6. **Run the bot:**
   ```bash
   python main.py
   ```

### 📁 Project Structure

```
money-tracker/
├── main.py           # Main bot file
├── database.py       # Database connection class
├── .env              # Environment variables (git ignored)
├── .gitignore        # Git ignored files
└── README.md         # This file
```

### 📝 License

This project is licensed under the MIT License.

### 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

</div>
