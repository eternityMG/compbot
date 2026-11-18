import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    async def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Таблица пользователей
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                                                         user_id INTEGER PRIMARY KEY,
                                                         username TEXT,
                                                         first_name TEXT,
                                                         registered_at TEXT
                    )
                    ''')

        # Таблица компонентов - УБЕДИСЬ ЧТО ЕСТЬ specifications
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS components (
                                                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                              type TEXT,
                                                              name TEXT,
                                                              brand TEXT,
                                                              model TEXT,
                                                              specifications TEXT,
                                                              price INTEGER,
                                                              in_stock INTEGER DEFAULT 1
                    )
                    ''')

        # Таблица сборок
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS configurations (
                                                                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                  user_id INTEGER,
                                                                  components TEXT,
                                                                  total_price INTEGER,
                                                                  created_at TEXT,
                                                                  shared_link TEXT
                    )
                    ''')

        # Таблица текущих сборок
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS current_config (
                                                                  user_id INTEGER PRIMARY KEY,
                                                                  components TEXT
                    )
                    ''')

        # Проверяем есть ли компоненты
        cur.execute("SELECT COUNT(*) FROM components")
        if cur.fetchone()[0] == 0:
            # Добавляем ВСЕ типы компонентов
            test_data = [
                # Процессоры
                ('cpu', 'Intel Core i5-12400F', 'Intel', 'i5-12400F', json.dumps({'Ядра': '6', 'Потоки': '12', 'Частота': '2.5 GHz'}), 15000, 1),
                ('cpu', 'Intel Core i7-12700K', 'Intel', 'i7-12700K', json.dumps({'Ядра': '12', 'Потоки': '20', 'Частота': '3.6 GHz'}), 30000, 1),
                ('cpu', 'AMD Ryzen 5 5600X', 'AMD', '5600X', json.dumps({'Ядра': '6', 'Потоки': '12', 'Частота': '3.7 GHz'}), 18000, 1),
                ('cpu', 'AMD Ryzen 7 5800X', 'AMD', '5800X', json.dumps({'Ядра': '8', 'Потоки': '16', 'Частота': '3.8 GHz'}), 28000, 1),

                # Видеокарты
                ('gpu', 'NVIDIA RTX 3060', 'NVIDIA', 'RTX 3060', json.dumps({'Память': '12 GB', 'Тип': 'GDDR6'}), 35000, 1),
                ('gpu', 'NVIDIA RTX 3070', 'NVIDIA', 'RTX 3070', json.dumps({'Память': '8 GB', 'Тип': 'GDDR6'}), 50000, 1),
                ('gpu', 'AMD RX 6600', 'AMD', 'RX 6600', json.dumps({'Память': '8 GB', 'Тип': 'GDDR6'}), 28000, 1),
                ('gpu', 'AMD RX 6700 XT', 'AMD', 'RX 6700 XT', json.dumps({'Память': '12 GB', 'Тип': 'GDDR6'}), 40000, 1),

                # Оперативная память
                ('ram', 'Kingston 16GB DDR4', 'Kingston', 'KVR16N11/8', json.dumps({'Объем': '16 GB', 'Тип': 'DDR4', 'Частота': '3200 MHz'}), 6000, 1),
                ('ram', 'Samsung 32GB DDR4', 'Samsung', 'M378A4G43AB1', json.dumps({'Объем': '32 GB', 'Тип': 'DDR4', 'Частота': '2666 MHz'}), 12000, 1),
                ('ram', 'Corsair 16GB DDR5', 'Corsair', 'CMK16GX5M1B5600C36', json.dumps({'Объем': '16 GB', 'Тип': 'DDR5', 'Частота': '5600 MHz'}), 9000, 1),

                # Материнские платы
                ('motherboard', 'ASUS Prime B660M-A', 'ASUS', 'B660M-A', json.dumps({'Сокет': 'LGA1700', 'Форм-фактор': 'mATX', 'Память': 'DDR4'}), 12000, 1),
                ('motherboard', 'MSI B550 Tomahawk', 'MSI', 'B550', json.dumps({'Сокет': 'AM4', 'Форм-фактор': 'ATX', 'Память': 'DDR4'}), 15000, 1),
                ('motherboard', 'Gigabyte Z690 Aorus', 'Gigabyte', 'Z690', json.dumps({'Сокет': 'LGA1700', 'Форм-фактор': 'ATX', 'Память': 'DDR5'}), 25000, 1),

                # Накопители
                ('storage', 'Samsung 980 500GB', 'Samsung', '980', json.dumps({'Объем': '500 GB', 'Тип': 'NVMe M.2'}), 6000, 1),
                ('storage', 'WD Blue 1TB', 'WD', 'Blue', json.dumps({'Объем': '1 TB', 'Тип': 'SATA III'}), 5000, 1),
                ('storage', 'Kingston A2000 1TB', 'Kingston', 'A2000', json.dumps({'Объем': '1 TB', 'Тип': 'NVMe M.2'}), 8000, 1),

                # Блоки питания
                ('psu', 'Corsair 650W', 'Corsair', 'CV650', json.dumps({'Мощность': '650W', 'Сертификат': '80+ Bronze'}), 7000, 1),
                ('psu', 'Chieftec 750W', 'Chieftec', 'GPE-750S', json.dumps({'Мощность': '750W', 'Сертификат': '80+ Gold'}), 9000, 1),
                ('psu', 'Seasonic 850W', 'Seasonic', 'FOCUS', json.dumps({'Мощность': '850W', 'Сертификат': '80+ Platinum'}), 15000, 1),

                # Корпуса
                ('case', 'Deepcool MATREXX 40', 'Deepcool', 'MATREXX 40', json.dumps({'Форм-фактор': 'mATX', 'Без БП': 'Да'}), 4000, 1),
                ('case', 'Zalman S2', 'Zalman', 'S2', json.dumps({'Форм-фактор': 'ATX', 'Без БП': 'Да'}), 5000, 1),
                ('case', 'NZXT H510', 'NZXT', 'H510', json.dumps({'Форм-фактор': 'ATX', 'Без БП': 'Да'}), 8000, 1),
            ]
            cur.executemany('''
                            INSERT INTO components (type, name, brand, model, specifications, price, in_stock)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', test_data)

        conn.commit()
        conn.close()

    async def add_user(self, user_id, first_name, username=None):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO users (user_id, username, first_name, registered_at) VALUES (?,?,?,?)",
            (user_id, username, first_name, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

    async def get_components_by_type(self, comp_type):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM components WHERE type=? AND in_stock=1", (comp_type,))
        rows = cur.fetchall()
        conn.close()

        components = []
        for row in rows:
            comp = dict(row)
            # Безопасно парсим specifications
            try:
                if comp['specifications']:
                    comp['specifications'] = json.loads(comp['specifications'])
                else:
                    comp['specifications'] = {}
            except:
                comp['specifications'] = {}
            components.append(comp)
        return components

    async def get_component(self, comp_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM components WHERE id=?", (comp_id,))
        row = cur.fetchone()
        conn.close()

        if row:
            comp = dict(row)
            # Безопасно парсим specifications
            try:
                if comp['specifications']:
                    comp['specifications'] = json.loads(comp['specifications'])
                else:
                    comp['specifications'] = {}
            except:
                comp['specifications'] = {}
            return comp
        return None

    async def add_component_to_config(self, user_id, comp_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("SELECT components FROM current_config WHERE user_id=?", (user_id,))
        row = cur.fetchone()

        if row:
            components = json.loads(row[0])
        else:
            components = []

        if comp_id not in components:
            components.append(comp_id)
            cur.execute(
                "INSERT OR REPLACE INTO current_config VALUES (?,?)",
                (user_id, json.dumps(components))
            )

        conn.commit()
        conn.close()

    async def finalize_configuration(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("SELECT components FROM current_config WHERE user_id=?", (user_id,))
        row = cur.fetchone()

        if not row:
            conn.close()
            return None

        comp_ids = json.loads(row[0])
        if not comp_ids:
            conn.close()
            return None

        # Получаем информацию о компонентах
        components = []
        total = 0
        for comp_id in comp_ids:
            cur.execute("SELECT name, price FROM components WHERE id=?", (comp_id,))
            result = cur.fetchone()
            if result:
                name, price = result
                components.append({'name': name, 'price': price})
                total += price

        # Сохраняем в историю
        created_at = datetime.now().isoformat()
        cur.execute(
            "INSERT INTO configurations (user_id, components, total_price, created_at) VALUES (?,?,?,?)",
            (user_id, json.dumps(comp_ids), total, created_at)
        )
        config_id = cur.lastrowid

        # Очищаем текущую сборку
        cur.execute("DELETE FROM current_config WHERE user_id=?", (user_id,))

        conn.commit()
        conn.close()

        return {
            'id': config_id,
            'components': components,
            'total_price': total,
            'created_at': created_at
        }

    async def get_user_configurations(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "SELECT id, total_price, created_at FROM configurations WHERE user_id=? ORDER BY created_at DESC LIMIT 5",
            (user_id,)
        )
        rows = cur.fetchall()
        conn.close()

        configs = []
        for row in rows:
            configs.append({
                'id': row[0],
                'total_price': row[1],
                'created_at': row[2]
            })
        return configs

    async def get_configuration(self, config_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM configurations WHERE id=?", (config_id,))
        row = cur.fetchone()

        if not row:
            conn.close()
            return None

        config = dict(row)
        comp_ids = json.loads(config['components'])

        components = []
        for comp_id in comp_ids:
            cur.execute("SELECT name, price FROM components WHERE id=?", (comp_id,))
            result = cur.fetchone()
            if result:
                name, price = result
                components.append({'name': name, 'price': price})

        config['components'] = components
        conn.close()
        return config

    async def update_config_link(self, config_id, link):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("UPDATE configurations SET shared_link=? WHERE id=?", (link, config_id))
        conn.commit()
        conn.close()