# core/database_manager.py
import sqlite3
import logging

# Logger für dieses Modul erstellen
logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path='data/klausur.db'):
        try:
            self.conn = sqlite3.connect(db_path, isolation_level=None)
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA foreign_keys = ON")
            logger.info("Datenbankverbindung im Autocommit-Modus hergestellt.")
        except sqlite3.Error as e:
            logger.error(f"Datenbankfehler bei der Verbindung: {e}")
            self.conn = None

    def setup_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE
            )''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pools (
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, module_id INTEGER NOT NULL,
                FOREIGN KEY (module_id) REFERENCES modules (id) ON DELETE CASCADE
            )''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT, content_md TEXT NOT NULL, pool_id INTEGER NOT NULL,
                FOREIGN KEY (pool_id) REFERENCES pools (id) ON DELETE CASCADE
            )''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS exam_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT, module_id INTEGER NOT NULL UNIQUE, pool_order TEXT NOT NULL,
                FOREIGN KEY (module_id) REFERENCES modules (id) ON DELETE CASCADE
            )''')
        logger.debug("Tabellen-Setup abgeschlossen.")

    def add_module(self, name):
        sql = "INSERT INTO modules (name) VALUES (?)"
        try:
            self.cursor.execute(sql, (name,))
            last_id = self.cursor.lastrowid
            logger.info(f"Modul '{name}' (ID: {last_id}) hinzugefügt.")
            return last_id
        except sqlite3.IntegrityError:
            logger.warning(f"Versuch, doppeltes Modul '{name}' hinzuzufügen.")
            return None

    def add_pool(self, name, module_id):
        sql = "INSERT INTO pools (name, module_id) VALUES (?, ?)"
        self.cursor.execute(sql, (name, module_id))
        last_id = self.cursor.lastrowid
        logger.info(f"Pool '{name}' (ID: {last_id}) zu Modul ID {module_id} hinzugefügt.")
        return last_id

    def add_task(self, content_md, pool_id):
        sql = "INSERT INTO tasks (content_md, pool_id) VALUES (?, ?)"
        self.cursor.execute(sql, (content_md, pool_id))
        last_id = self.cursor.lastrowid
        logger.info(f"Aufgabe (ID: {last_id}) zu Pool ID {pool_id} hinzugefügt.")
        return last_id

    def update_task(self, task_id, new_content):
        sql = "UPDATE tasks SET content_md = ? WHERE id = ?"
        self.cursor.execute(sql, (new_content, task_id))
        logger.info(f"Aufgabe ID {task_id} aktualisiert.")

    def delete_module(self, module_id):
        self.cursor.execute("DELETE FROM modules WHERE id = ?", (module_id,))
        logger.info(f"Modul ID {module_id} gelöscht.")

    def delete_pool(self, pool_id):
        self.cursor.execute("DELETE FROM pools WHERE id = ?", (pool_id,))
        logger.info(f"Pool ID {pool_id} gelöscht.")

    def delete_task(self, task_id):
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        logger.info(f"Aufgabe ID {task_id} gelöscht.")

    def get_modules(self):
        self.cursor.execute("SELECT id, name FROM modules ORDER BY name")
        return self.cursor.fetchall()

    def get_pools_for_module(self, module_id):
        self.cursor.execute("SELECT id, name FROM pools WHERE module_id = ? ORDER BY name", (module_id,))
        return self.cursor.fetchall()

    def get_tasks_from_pool(self, pool_id):
        self.cursor.execute("SELECT id, content_md FROM tasks WHERE pool_id = ?", (pool_id,))
        return self.cursor.fetchall()

    def save_exam_config(self, module_id, pool_order_str):
        sql = "INSERT OR REPLACE INTO exam_configs (module_id, pool_order) VALUES (?, ?)"
        self.cursor.execute(sql, (module_id, pool_order_str))
        logger.info(f"Klausurkonfiguration für Modul ID {module_id} gespeichert.")

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("Datenbankverbindung geschlossen.")