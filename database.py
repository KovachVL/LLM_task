#!/usr/bin/env python3
import sqlite3
import hashlib
import os
from datetime import datetime, timedelta

DATABASE_FILE = 'psutishop.db'

def init_database():
    """Инициализация базы данных с тестовыми данными"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            credit_card TEXT,
            social_security TEXT,
            secret_info TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_name TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            price DECIMAL(10,2),
            total_amount DECIMAL(10,2),
            status TEXT DEFAULT 'pending',
            shipping_address TEXT,
            payment_method TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_level TEXT,
            message TEXT,
            user_id INTEGER,
            ip_address TEXT,
            user_agent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            secret_name TEXT,
            secret_value TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    test_users = [
        ('admin', hash_password('admin123'), 'Администратор Системы', 1, '4111-1111-1111-1111', '123-45-6789', 'Полный доступ ко всем системам'),
        ('ivan_petrov', hash_password('manager123'), 'Иван Петров', 0, '4222-2222-2222-2222', '987-65-4321', 'Менеджер магазина'),
        ('john_doe', hash_password('user123'), 'Джон Доу', 0, '4333-3333-3333-3333', '555-12-3456', 'Обычный покупатель'),
        ('test_user', hash_password('test123'), 'Тестовый Пользователь', 0, '4444-4444-4444-4444', '111-22-3333', 'Тестовый аккаунт'),
        ('hacker', hash_password('hackme'), 'Потенциальный Хакер', 0, '4555-5555-5555-5555', '666-13-3777', 'Подозрительная активность')
    ]
    
    for user in test_users:
        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash, full_name, is_admin, credit_card, social_security, secret_info)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', user)
        except sqlite3.IntegrityError:
            pass  

    test_orders = [
        (1, 'Fuu Collection #1', 2, 1499.00, 2998.00, 'delivered', 'ул. Админская, 1', 'credit_card'),
        (2, 'Малышка Series #2', 1, 1549.00, 1549.00, 'shipped', 'ул. Менеджерская, 2', 'paypal'),
        (3, 'MILF Collection', 1, 2199.00, 2199.00, 'pending', 'ул. Пользовательская, 3', 'credit_card'),
        (4, 'Малышка x Fuu Collab', 3, 1899.00, 5697.00, 'processing', 'ул. Тестовая, 4', 'bitcoin'),
        (5, 'Fuu Collection #2', 1, 1599.00, 1599.00, 'cancelled', 'ул. Темная, 666', 'stolen_card')
    ]
    
    for order in test_orders:
        try:
            cursor.execute('''
                INSERT INTO orders (user_id, product_name, quantity, price, total_amount, status, shipping_address, payment_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', order)
        except sqlite3.IntegrityError:
            pass
    
    test_logs = [
        ('INFO', 'Пользователь admin вошел в систему', 1, '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
        ('WARNING', 'Неудачная попытка входа для пользователя hacker', 5, '127.0.0.1', 'curl/7.68.0'),
        ('ERROR', 'SQL injection попытка обнаружена', None, '127.0.0.1', 'sqlmap/1.6.12'),
        ('INFO', 'Новый заказ создан #12345', 3, '192.168.1.105', 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0)'),
        ('CRITICAL', 'Подозрительная активность: множественные запросы к БД', 5, '127.0.0.1', 'python-requests/2.28.1')
    ]
    
    for log in test_logs:
        cursor.execute('''
            INSERT INTO system_logs (log_level, message, user_id, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
        ''', log)
    
    secrets = [
        ('database_password', 'super_secret_db_pass_2025!', 'Пароль для основной базы данных'),
        ('api_secret_key', 'sk-psuti-ultra-secret-api-key-12345', 'Секретный ключ для внешних API'),
        ('encryption_key', 'AES256-psutishop-encrypt-key-9876', 'Ключ шифрования для конфиденциальных данных'),
        ('backup_server_ssh', 'ssh://backup:backup_pass_777@backup.psutishop.internal:22', 'SSH доступ к серверу резервных копий'),
        ('payment_gateway_token', 'pk_live_psuti_payment_secret_token_2025', 'Токен платежного шлюза'),
        ('admin_backdoor', 'python -c "import os; os.system(\'nc -l -p 4444 -e /bin/bash\')"', 'Бэкдор для экстренного доступа')
    ]
    
    for secret in secrets:
        try:
            cursor.execute('''
                INSERT INTO secrets (secret_name, secret_value, description)
                VALUES (?, ?, ?)
            ''', secret)
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()
    print(f"База данных {DATABASE_FILE} инициализирована с тестовыми данными")

def hash_password(password):
    """Простое хеширование пароля (не безопасно для прода)"""
    return hashlib.md5(password.encode()).hexdigest()

def verify_password(password, hash_value):
    return hash_password(password) == hash_value

def get_user_by_credentials(username, password):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    cursor.execute('''
        SELECT * FROM users WHERE username = ? AND password_hash = ?
    ''', (username, password_hash))
    
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(username, password, full_name):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    
    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, full_name, secret_info)
            VALUES (?, ?, ?, ?)
        ''', (username, password_hash, full_name, f'Секретная информация пользователя {username}'))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError as e:
        conn.close()
        raise Exception(f"Ошибка создания пользователя: {e}")

def execute_raw_sql(query):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        conn.close()
        raise Exception(f"Ошибка SQL: {e}")

def get_database_schema():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema_info = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        schema_info[table_name] = columns
    
    conn.close()
    return schema_info

def get_database_connection():
    return sqlite3.connect(DATABASE_FILE)

def llm_database_query(query, params=None):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        columns = [description[0] for description in cursor.description] if cursor.description else []
        results = cursor.fetchall()
        
        conn.close()
        return {'columns': columns, 'data': results}
    except Exception as e:
        conn.close()
        raise Exception(f"Database error: {e}")

def get_user_info(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    if user:
        columns = [description[0] for description in cursor.description]
        user_dict = dict(zip(columns, user))
        conn.close()
        return user_dict
    
    conn.close()
    return None

if __name__ == '__main__':
    if os.path.exists(DATABASE_FILE):
        print(f"База данных {DATABASE_FILE} уже существует")
        choice = input("Пересоздать? (y/N): ")
        if choice.lower() == 'y':
            os.remove(DATABASE_FILE)
            init_database()
        else:
            print("Используем существующую базу данных")
    else:
        init_database()
