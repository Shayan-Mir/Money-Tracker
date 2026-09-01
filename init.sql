CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    period_start_date DATETIME
);

CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type ENUM('income', 'expense', 'investment') NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    description TEXT,
    date DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS investments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transactions_id INT NOT NULL,
    asset_type ENUM('gold', 'silver', 'coin', 'usd', 'eur', 'bitcoin', 'other') NOT NULL,
    unit_amount DECIMAL(15, 4),
    custom_name VARCHAR(255),
    FOREIGN KEY (transactions_id) REFERENCES transactions(id)
);
