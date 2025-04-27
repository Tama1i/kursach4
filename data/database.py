import sqlite3
import pandas as pd
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_name='efficiency.db'):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS results
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                          efficiency REAL,
                          profit REAL,
                          costs REAL,
                          investments REAL,
                          market_share REAL,
                          economic_stability REAL,
                          tax_rate REAL)''')

    def save_results(self, data):
        """Сохраняет результаты расчета в базу данных"""
        with sqlite3.connect(self.db_name) as conn:
            data.to_sql('results', conn, if_exists='append', index=False)

    def load_recent_results(self, limit=12):
        """Загружает последние результаты из базы данных"""
        with sqlite3.connect(self.db_name) as conn:
            return pd.read_sql(
                f"SELECT * FROM results ORDER BY timestamp DESC LIMIT {limit}",
                conn
            )

    def export_to_csv(self, filename):
        """Экспортирует данные в CSV файл"""
        with sqlite3.connect(self.db_name) as conn:
            df = pd.read_sql("SELECT * FROM results", conn)
            df.to_csv(filename, index=False)