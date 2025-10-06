# core/database_manager.py
import sqlite3


class DatabaseManager:
    def __init__(self, db_path='data/klausur.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        # WICHTIG: Fremdschlüssel-Unterstützung für kaskadierendes Löschen aktivieren
        self.cursor.execute("PRAGMA foreign_keys = ON")
        print("✅ Datenbankverbindung erfolgreich hergestellt.")

    def setup_database(self):
        # Wir fügen "ON DELETE CASCADE" hinzu.
        # Das sorgt dafür, dass die Datenbank das Löschen von verknüpften Einträgen automatisch übernimmt.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                module_id INTEGER NOT NULL,
                FOREIGN KEY (module_id) REFERENCES modules (id) ON DELETE CASCADE
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_md TEXT NOT NULL,
                pool_id INTEGER NOT NULL,
                FOREIGN KEY (pool_id) REFERENCES pools (id) ON DELETE CASCADE
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS exam_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER NOT NULL UNIQUE,
                pool_order TEXT NOT NULL,
                FOREIGN KEY (module_id) REFERENCES modules (id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()
        print("👍 Tabellen erfolgreich eingerichtet.")

    # --- Hinzufügen von Daten (unverändert) ---
    def add_module(self, name):
        sql = "INSERT INTO modules (name) VALUES (?)"
        try:
            self.cursor.execute(sql, (name,))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Warnung: Modul '{name}' existiert bereits.")
            return None

    def add_pool(self, name, module_id):
        sql = "INSERT INTO pools (name, module_id) VALUES (?, ?)"
        self.cursor.execute(sql, (name, module_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_task(self, content_md, pool_id):
        sql = "INSERT INTO tasks (content_md, pool_id) VALUES (?, ?)"
        self.cursor.execute(sql, (content_md, pool_id))
        self.conn.commit()
        return self.cursor.lastrowid

    # --- Abrufen von Daten (unverändert) ---
    def get_modules(self):
        self.cursor.execute("SELECT id, name FROM modules ORDER BY name")
        return self.cursor.fetchall()

    def get_pools_for_module(self, module_id):
        self.cursor.execute("SELECT id, name FROM pools WHERE module_id = ? ORDER BY name", (module_id,))
        return self.cursor.fetchall()

    def get_tasks_from_pool(self, pool_id):
        self.cursor.execute("SELECT id, content_md FROM tasks WHERE pool_id = ?", (pool_id,))
        return self.cursor.fetchall()

    # --- LÖSCHFUNKTIONEN (NEU) ---
    def delete_module(self, module_id):
        """Löscht ein Modul. Dank ON DELETE CASCADE werden alle zugehörigen Pools/Tasks mitgelöscht."""
        self.cursor.execute("DELETE FROM modules WHERE id = ?", (module_id,))
        self.conn.commit()

    def delete_pool(self, pool_id):
        """Löscht einen Pool. Dank ON DELETE CASCADE werden alle zugehörigen Tasks mitgelöscht."""
        self.cursor.execute("DELETE FROM pools WHERE id = ?", (pool_id,))
        self.conn.commit()

    def delete_task(self, task_id):
        """Löscht eine einzelne Aufgabe."""
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()

    # --- Hilfsfunktionen (unverändert) ---
    def get_module_by_id(self, module_id):
        self.cursor.execute("SELECT id, name FROM modules WHERE id = ?", (module_id,))
        return self.cursor.fetchone()

    def get_exam_config_for_module(self, module_id):
        self.cursor.execute("SELECT id, module_id, pool_order FROM exam_configs WHERE module_id = ?", (module_id,))
        return self.cursor.fetchone()

    def save_exam_config(self, module_id, pool_order_str):
        sql = "INSERT OR REPLACE INTO exam_configs (module_id, pool_order) VALUES (?, ?)"
        self.cursor.execute(sql, (module_id, pool_order_str))
        self.conn.commit()

    def update_task(self, task_id, new_content):
        """Aktualisiert den Inhalt einer bestehenden Aufgabe."""
        sql = "UPDATE tasks SET content_md = ? WHERE id = ?"
        self.cursor.execute(sql, (new_content, task_id))
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
            print("🔌 Datenbankverbindung geschlossen.")