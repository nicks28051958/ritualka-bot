import sqlite3
import asyncio
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица анкет похорон
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS funeral_forms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                body_location TEXT,
                funeral_type TEXT,
                services TEXT,
                budget TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
            )
        ''')
        
        # Таблица товаров
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL,
                category TEXT,
                photo_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица записей памяти
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                name TEXT NOT NULL,
                birth_date TEXT,
                death_date TEXT,
                memory_text TEXT,
                photo_path TEXT,
                html_path TEXT,
                candles_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
            )
        ''')
        
        # Таблица свечей памяти
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_candles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_record_id INTEGER,
                telegram_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memory_record_id) REFERENCES memory_records (id),
                FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
            )
        ''')
        
        # Таблица логов запросов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                request_type TEXT,
                request_data TEXT,
                response_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
            )
        ''')
        
        # Таблица логов диалогов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                message_type TEXT,
                message_text TEXT,
                handler_name TEXT,
                is_user_message BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
            )
        ''')
        
        # Таблица клиентов с полными реквизитами
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                full_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                birth_date TEXT,
                passport_series TEXT,
                passport_number TEXT,
                passport_issued_by TEXT,
                passport_issue_date TEXT,
                address TEXT,
                emergency_contact TEXT,
                relationship TEXT,
                is_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Инициализация товаров
        self.init_products()
    
    def init_products(self):
        """Инициализация товаров в базе данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже товары
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            products = [
                # Гробы
                ("Гроб деревянный стандартный", "Классический деревянный гроб из сосны", 15000, "coffin", "photos/coffin1.jpg"),
                ("Гроб деревянный премиум", "Гроб из дуба с резными элементами", 25000, "coffin", "photos/coffin2.jpg"),
                ("Гроб металлический", "Металлический гроб с отделкой", 35000, "coffin", "photos/coffin3.jpg"),
                ("Гроб детский", "Детский гроб из дерева", 8000, "coffin", "photos/coffin4.jpg"),
                
                # Венки
                ("Венок траурный стандартный", "Классический траурный венок", 3000, "wreath", "photos/wreath1.jpg"),
                ("Венок премиум", "Венок из живых цветов", 8000, "wreath", "photos/wreath2.jpg"),
                ("Венок детский", "Небольшой венок для детей", 2000, "wreath", "photos/wreath3.jpg"),
                
                # Кресты
                ("Крест деревянный", "Деревянный крест для могилы", 5000, "cross", "photos/cross1.jpg"),
                ("Крест металлический", "Металлический крест с покрытием", 12000, "cross", "photos/cross2.jpg"),
                ("Крест гранитный", "Гранитный крест", 25000, "cross", "photos/cross3.jpg"),
            ]
            
            cursor.executemany(
                "INSERT INTO products (name, description, price, category, photo_path) VALUES (?, ?, ?, ?, ?)",
                products
            )
            
            conn.commit()
        
        conn.close()
    
    async def add_user(self, telegram_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Добавление пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (telegram_id, username, first_name, last_name, last_activity)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (telegram_id, username, first_name, last_name))
        
        conn.commit()
        conn.close()
    
    async def save_funeral_form(self, telegram_id: int, body_location: str, funeral_type: str, services: List[str], budget: str):
        """Сохранение анкеты похорон"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        services_json = json.dumps(services)
        
        cursor.execute('''
            INSERT INTO funeral_forms (telegram_id, body_location, funeral_type, services, budget)
            VALUES (?, ?, ?, ?, ?)
        ''', (telegram_id, body_location, funeral_type, services_json, budget))
        
        conn.commit()
        conn.close()
    
    async def get_products_by_category(self, category: str = None) -> List[Dict]:
        """Получение товаров по категории"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
        else:
            cursor.execute("SELECT * FROM products")
        
        products = []
        for row in cursor.fetchall():
            products.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'price': row[3],
                'category': row[4],
                'photo_path': row[5]
            })
        
        conn.close()
        return products
    
    async def create_memory_record(self, telegram_id: int, name: str, birth_date: str, death_date: str, memory_text: str, photo_path: str, html_path: str):
        """Создание записи памяти"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO memory_records (telegram_id, name, birth_date, death_date, memory_text, photo_path, html_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (telegram_id, name, birth_date, death_date, memory_text, photo_path, html_path))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return record_id
    
    async def add_candle(self, memory_record_id: int, telegram_id: int):
        """Добавление свечи к записи памяти"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Проверяем, не зажигал ли уже этот пользователь свечу
        cursor.execute('''
            SELECT id FROM memory_candles 
            WHERE memory_record_id = ? AND telegram_id = ?
        ''', (memory_record_id, telegram_id))
        
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO memory_candles (memory_record_id, telegram_id)
                VALUES (?, ?)
            ''', (memory_record_id, telegram_id))
            
            # Увеличиваем счетчик свечей
            cursor.execute('''
                UPDATE memory_records 
                SET candles_count = candles_count + 1 
                WHERE id = ?
            ''', (memory_record_id,))
            
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    
    async def get_memory_records(self, telegram_id: int = None) -> List[Dict]:
        """Получение записей памяти"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if telegram_id:
            cursor.execute('''
                SELECT mr.*, COUNT(mc.id) as candles_count 
                FROM memory_records mr 
                LEFT JOIN memory_candles mc ON mr.id = mc.memory_record_id 
                WHERE mr.telegram_id = ? 
                GROUP BY mr.id
            ''', (telegram_id,))
        else:
            cursor.execute('''
                SELECT mr.*, COUNT(mc.id) as candles_count 
                FROM memory_records mr 
                LEFT JOIN memory_candles mc ON mr.id = mc.memory_record_id 
                GROUP BY mr.id
            ''')
        
        records = []
        for row in cursor.fetchall():
            records.append({
                'id': row[0],
                'telegram_id': row[1],
                'name': row[2],
                'birth_date': row[3],
                'death_date': row[4],
                'memory_text': row[5],
                'photo_path': row[6],
                'html_path': row[7],
                'candles_count': row[8],
                'created_at': row[9]
            })
        
        conn.close()
        return records
    
    async def log_request(self, telegram_id: int, request_type: str, request_data: str, response_data: str = None):
        """Логирование запросов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO request_logs (telegram_id, request_type, request_data, response_data)
            VALUES (?, ?, ?, ?)
        ''', (telegram_id, request_type, request_data, response_data))
        
        conn.commit()
        conn.close()
    
    async def get_user_stats(self) -> Dict:
        """Получение статистики пользователей"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Общее количество пользователей
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Активные пользователи за последние 7 дней
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE last_activity > datetime('now', '-7 days')
        """)
        active_users = cursor.fetchone()[0]
        
        # Количество анкет
        cursor.execute("SELECT COUNT(*) FROM funeral_forms")
        total_forms = cursor.fetchone()[0]
        
        # Количество записей памяти
        cursor.execute("SELECT COUNT(*) FROM memory_records")
        total_memories = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'total_forms': total_forms,
            'total_memories': total_memories
        }
    
    async def log_chat_message(self, telegram_id: int, message_type: str, message_text: str, handler_name: str, is_user_message: bool):
        """Логирование сообщений диалога"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_logs (telegram_id, message_type, message_text, handler_name, is_user_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (telegram_id, message_type, message_text, handler_name, is_user_message))
        
        conn.commit()
        conn.close()
    
    async def get_chat_logs(self, telegram_id: int = None, limit: int = 100) -> List[Dict]:
        """Получение логов диалогов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if telegram_id:
            cursor.execute('''
                SELECT cl.*, u.username, u.first_name 
                FROM chat_logs cl 
                LEFT JOIN users u ON cl.telegram_id = u.telegram_id
                WHERE cl.telegram_id = ? 
                ORDER BY cl.created_at DESC 
                LIMIT ?
            ''', (telegram_id, limit))
        else:
            cursor.execute('''
                SELECT cl.*, u.username, u.first_name 
                FROM chat_logs cl 
                LEFT JOIN users u ON cl.telegram_id = u.telegram_id
                ORDER BY cl.created_at DESC 
                LIMIT ?
            ''', (limit,))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                'id': row[0],
                'telegram_id': row[1],
                'message_type': row[2],
                'message_text': row[3],
                'handler_name': row[4],
                'is_user_message': bool(row[5]),
                'created_at': row[6],
                'username': row[7],
                'first_name': row[8]
            })
        
        conn.close()
        return logs
    
    # Методы для работы с клиентами
    async def save_client_data(self, telegram_id: int, **kwargs) -> bool:
        """Сохранение данных клиента"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Проверяем, существует ли уже клиент
            cursor.execute("SELECT id FROM clients WHERE telegram_id = ?", (telegram_id,))
            existing_client = cursor.fetchone()
            
            if existing_client:
                # Обновляем существующего клиента
                update_fields = []
                values = []
                for key, value in kwargs.items():
                    if value is not None:
                        update_fields.append(f"{key} = ?")
                        values.append(value)
                
                if update_fields:
                    update_fields.append("updated_at = CURRENT_TIMESTAMP")
                    values.append(telegram_id)
                    
                    query = f"UPDATE clients SET {', '.join(update_fields)} WHERE telegram_id = ?"
                    cursor.execute(query, values)
            else:
                # Создаем нового клиента
                fields = ['telegram_id'] + list(kwargs.keys())
                placeholders = ['?'] * len(fields)
                values = [telegram_id] + list(kwargs.values())
                
                query = f"INSERT INTO clients ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
                cursor.execute(query, values)
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            conn.close()
            print(f"Ошибка при сохранении данных клиента: {e}")
            return False
    
    async def get_client_data(self, telegram_id: int) -> Optional[Dict]:
        """Получение данных клиента"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM clients WHERE telegram_id = ?
        ''', (telegram_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'telegram_id': row[1],
                'full_name': row[2],
                'phone': row[3],
                'email': row[4],
                'birth_date': row[5],
                'passport_series': row[6],
                'passport_number': row[7],
                'passport_issued_by': row[8],
                'passport_issue_date': row[9],
                'address': row[10],
                'emergency_contact': row[11],
                'relationship': row[12],
                'is_verified': bool(row[13]),
                'created_at': row[14],
                'updated_at': row[15]
            }
        return None
    
    async def is_client_registered(self, telegram_id: int) -> bool:
        """Проверка, зарегистрирован ли клиент"""
        client_data = await self.get_client_data(telegram_id)
        return client_data is not None
    
    async def get_all_clients(self) -> List[Dict]:
        """Получение всех клиентов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, u.username, u.first_name, u.last_name 
            FROM clients c 
            LEFT JOIN users u ON c.telegram_id = u.telegram_id
            ORDER BY c.created_at DESC
        ''')
        
        clients = []
        for row in cursor.fetchall():
            clients.append({
                'id': row[0],
                'telegram_id': row[1],
                'full_name': row[2],
                'phone': row[3],
                'email': row[4],
                'birth_date': row[5],
                'passport_series': row[6],
                'passport_number': row[7],
                'passport_issued_by': row[8],
                'passport_issue_date': row[9],
                'address': row[10],
                'emergency_contact': row[11],
                'relationship': row[12],
                'is_verified': bool(row[13]),
                'created_at': row[14],
                'updated_at': row[15],
                'username': row[16],
                'first_name': row[17],
                'last_name': row[18]
            })
        
        conn.close()
        return clients
    
    async def verify_client(self, telegram_id: int) -> bool:
        """Верификация клиента"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE clients SET is_verified = TRUE, updated_at = CURRENT_TIMESTAMP 
                WHERE telegram_id = ?
            ''', (telegram_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            conn.close()
            print(f"Ошибка при верификации клиента: {e}")
            return False 