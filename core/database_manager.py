# core/database_manager.py
import sqlite3


class DatabaseManager:
    def __init__(self, db_path='data/klausur.db'):
        """Initialisiert den Datenbank-Manager und verbindet sich mit der DB."""
        try:
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            print("✅ Datenbankverbindung erfolgreich hergestellt.")
        except sqlite3.Error as e:
            print(f"❌ Datenbankfehler: {e}")
            self.conn = None

    def setup_database(self):
        """Erstellt die notwendigen Tabellen, falls sie nicht existieren."""
        if not self.conn:
            return

        try:
            # Module Tabelle
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS modules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            ''')
            # Aufgabenpools Tabelle
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS pools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    module_id INTEGER NOT NULL,
                    FOREIGN KEY (module_id) REFERENCES modules (id)
                )
            ''')
            # Aufgaben Tabelle
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_md TEXT NOT NULL,
                    pool_id INTEGER NOT NULL,
                    FOREIGN KEY (pool_id) REFERENCES pools (id)
                )
            ''')
            # Klausurkonfigurationen Tabelle
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS exam_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    module_id INTEGER NOT NULL UNIQUE,
                    pool_order TEXT NOT NULL,
                    FOREIGN KEY (module_id) REFERENCES modules (id)
                )
            ''')
            self.conn.commit()
            print("👍 Tabellen erfolgreich eingerichtet.")
        except sqlite3.Error as e:
            print(f"❌ Fehler beim Einrichten der Tabellen: {e}")

    # --- Methoden zum Hinzufügen von Daten ---
    def add_module(self, name):
        """Fügt ein neues Modul hinzu."""
        sql = "INSERT INTO modules (name) VALUES (?)"
        try:
            self.cursor.execute(sql, (name,))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Warnung: Modul '{name}' existiert bereits.")
            return None

    def add_pool(self, name, module_id):
        """Fügt einen neuen Aufgabenpool zu einem Modul hinzu."""
        sql = "INSERT INTO pools (name, module_id) VALUES (?, ?)"
        self.cursor.execute(sql, (name, module_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_task(self, content_md, pool_id):
        """Fügt eine neue Aufgabe zu einem Pool hinzu."""
        sql = "INSERT INTO tasks (content_md, pool_id) VALUES (?, ?)"
        self.cursor.execute(sql, (content_md, pool_id))
        self.conn.commit()
        return self.cursor.lastrowid

    # --- Methoden zum Abrufen von Daten ---
    def get_modules(self):
        """Gibt eine Liste aller Module als Tupel (id, name) zurück."""
        self.cursor.execute("SELECT id, name FROM modules ORDER BY name")
        return self.cursor.fetchall()

    def get_pools_for_module(self, module_id):
        """Gibt alle Pools für eine gegebene Modul-ID zurück."""
        self.cursor.execute("SELECT id, name FROM pools WHERE module_id = ? ORDER BY name", (module_id,))
        return self.cursor.fetchall()

    def get_tasks_from_pool(self, pool_id):
        """Gibt alle Aufgaben für eine gegebene Pool-ID zurück."""
        self.cursor.execute("SELECT id, content_md FROM tasks WHERE pool_id = ?", (pool_id,))
        return self.cursor.fetchall()

    def close(self):
        """Schließt die Datenbankverbindung."""
        if self.conn:
            self.conn.close()
            print("🔌 Datenbankverbindung geschlossen.")

    def get_module_by_id(self, module_id):
        """Holt ein einzelnes Modul anhand seiner ID."""
        self.cursor.execute("SELECT id, name FROM modules WHERE id = ?", (module_id,))
        return self.cursor.fetchone() # fetchone() statt fetchall()

    def get_exam_config_for_module(self, module_id):
        """Holt die Klausurkonfiguration für ein Modul."""
        self.cursor.execute("SELECT id, module_id, pool_order FROM exam_configs WHERE module_id = ?", (module_id,))
        return self.cursor.fetchone()

    def save_exam_config(self, module_id, pool_order_str):
        """Speichert oder aktualisiert eine Klausurkonfiguration."""
        # UNIQUE auf module_id sorgt dafür, dass REPLACE wie ein UPDATE funktioniert
        sql = "INSERT OR REPLACE INTO exam_configs (module_id, pool_order) VALUES (?, ?)"
        self.cursor.execute(sql, (module_id, pool_order_str))
        self.conn.commit()