# core/database_manager.py
import sqlite3
import os
import logging
from typing import Tuple, List, Optional

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: str = 'data/klausur.db'):
        """
        Robuster DatabaseManager:
         - speichert den db_path in self.db_path (Fix für deinen Fehler)
         - öffnet pro Operation eine Verbindung (thread-safe)
        """
        self.db_path = db_path
        # stelle sicher, dass das Verzeichnis existiert
        db_dir = os.path.dirname(os.path.abspath(self.db_path))
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
                logger.debug(f"Erstelle Datenbank-Verzeichnis: {db_dir}")
            except Exception as e:
                logger.exception(f"Fehler beim Erstellen des DB-Verzeichnisses {db_dir}: {e}")

        logger.debug(f"DatabaseManager initialisiert mit db_path={self.db_path}")

    # --- interne Helfer ---
    def _connect(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        """
        Öffnet eine neue Verbindung und liefert (conn, cursor).
        Wir setzen PRAGMA foreign_keys = ON für jede Verbindung.
        """
        conn = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()
        return conn, cur

    # --- Setup ---
    def setup_database(self):
        """Erstellt Tabellen, falls sie noch nicht existieren."""
        try:
            conn, cur = self._connect()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS modules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS pools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    module_id INTEGER NOT NULL,
                    FOREIGN KEY (module_id) REFERENCES modules (id) ON DELETE CASCADE
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_md TEXT NOT NULL,
                    pool_id INTEGER NOT NULL,
                    FOREIGN KEY (pool_id) REFERENCES pools (id) ON DELETE CASCADE
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS exam_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    module_id INTEGER NOT NULL UNIQUE,
                    pool_order TEXT NOT NULL,
                    FOREIGN KEY (module_id) REFERENCES modules (id) ON DELETE CASCADE
                )
            ''')
            conn.commit()
            conn.close()
            logger.info("Tabellen-Setup abgeschlossen (oder bereits vorhanden).")
        except Exception as e:
            logger.exception(f"Fehler beim Setup der Datenbank: {e}")
            raise

    # --- CRUD / Query-Methoden ---
    def add_module(self, name: str) -> Optional[int]:
        try:
            conn, cur = self._connect()
            cur.execute("INSERT INTO modules (name) VALUES (?)", (name,))
            last_id = cur.lastrowid
            conn.commit()
            conn.close()
            logger.info(f"Modul '{name}' (ID: {last_id}) hinzugefügt.")
            return last_id
        except sqlite3.IntegrityError:
            logger.warning(f"Versuch, doppeltes Modul '{name}' hinzuzufügen.")
            return None
        except Exception as e:
            logger.exception(f"Fehler beim Hinzufügen des Moduls '{name}': {e}")
            return None

    def add_pool(self, name: str, module_id: int) -> Optional[int]:
        try:
            conn, cur = self._connect()
            cur.execute("INSERT INTO pools (name, module_id) VALUES (?, ?)", (name, module_id))
            last_id = cur.lastrowid
            conn.commit()
            conn.close()
            logger.info(f"Pool '{name}' (ID: {last_id}) zu Modul ID {module_id} hinzugefügt.")
            return last_id
        except Exception as e:
            logger.exception(f"Fehler beim Hinzufügen des Pools '{name}' für Modul {module_id}: {e}")
            return None

    def add_task(self, content_md: str, pool_id: int) -> Optional[int]:
        try:
            conn, cur = self._connect()
            cur.execute("INSERT INTO tasks (content_md, pool_id) VALUES (?, ?)", (content_md, pool_id))
            last_id = cur.lastrowid
            conn.commit()
            conn.close()
            logger.info(f"Aufgabe (ID: {last_id}) zu Pool ID {pool_id} hinzugefügt.")
            return last_id
        except Exception as e:
            logger.exception(f"Fehler beim Hinzufügen einer Aufgabe zu Pool {pool_id}: {e}")
            return None

    def update_task(self, task_id: int, new_content: str) -> bool:
        try:
            conn, cur = self._connect()
            cur.execute("UPDATE tasks SET content_md = ? WHERE id = ?", (new_content, task_id))
            conn.commit()
            conn.close()
            logger.info(f"Aufgabe ID {task_id} aktualisiert.")
            return True
        except Exception as e:
            logger.exception(f"Fehler beim Aktualisieren der Aufgabe {task_id}: {e}")
            return False

    def delete_module(self, module_id: int) -> bool:
        try:
            conn, cur = self._connect()
            cur.execute("DELETE FROM modules WHERE id = ?", (module_id,))
            conn.commit()
            conn.close()
            logger.info(f"Modul ID {module_id} gelöscht.")
            return True
        except Exception as e:
            logger.exception(f"Fehler beim Löschen des Moduls {module_id}: {e}")
            return False

    def delete_pool(self, pool_id: int) -> bool:
        try:
            conn, cur = self._connect()
            cur.execute("DELETE FROM pools WHERE id = ?", (pool_id,))
            conn.commit()
            conn.close()
            logger.info(f"Pool ID {pool_id} gelöscht.")
            return True
        except Exception as e:
            logger.exception(f"Fehler beim Löschen des Pools {pool_id}: {e}")
            return False

    def delete_task(self, task_id: int) -> bool:
        try:
            conn, cur = self._connect()
            cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            conn.close()
            logger.info(f"Aufgabe ID {task_id} gelöscht.")
            return True
        except Exception as e:
            logger.exception(f"Fehler beim Löschen der Aufgabe {task_id}: {e}")
            return False

    def get_modules(self) -> List[tuple]:
        try:
            conn, cur = self._connect()
            cur.execute("SELECT id, name FROM modules ORDER BY name")
            rows = cur.fetchall()
            conn.close()
            return rows
        except Exception as e:
            logger.exception(f"get_modules Fehler: {e}")
            return []

    def get_pools_for_module(self, module_id: int) -> List[tuple]:
        try:
            conn, cur = self._connect()
            cur.execute("SELECT id, name FROM pools WHERE module_id = ? ORDER BY name", (module_id,))
            rows = cur.fetchall()
            conn.close()
            return rows
        except Exception as e:
            logger.exception(f"get_pools_for_module Fehler: {e}")
            return []

    def get_tasks_from_pool(self, pool_id: int) -> List[tuple]:
        try:
            conn, cur = self._connect()
            cur.execute("SELECT id, content_md FROM tasks WHERE pool_id = ?", (pool_id,))
            rows = cur.fetchall()
            conn.close()
            return rows
        except Exception as e:
            logger.exception(f"get_tasks_from_pool Fehler: {e}")
            return []

    # --- zusätzliche Methoden ---
    def get_module_by_id(self, module_id: int) -> Optional[tuple]:
        try:
            conn, cur = self._connect()
            cur.execute("SELECT id, name FROM modules WHERE id = ?", (module_id,))
            row = cur.fetchone()
            conn.close()
            return row
        except Exception as e:
            logger.exception(f"get_module_by_id Fehler: {e}")
            return None

    def get_pool_with_module_info(self, pool_id: int) -> Optional[tuple]:
        try:
            conn, cur = self._connect()
            cur.execute('''
                SELECT p.id, p.name, p.module_id, m.name
                FROM pools p
                LEFT JOIN modules m ON p.module_id = m.id
                WHERE p.id = ?
            ''', (pool_id,))
            row = cur.fetchone()
            conn.close()
            return row
        except Exception as e:
            logger.exception(f"get_pool_with_module_info Fehler: {e}")
            return None

    def get_exam_config_for_module(self, module_id: int) -> Optional[tuple]:
        try:
            conn, cur = self._connect()
            cur.execute("SELECT id, module_id, pool_order FROM exam_configs WHERE module_id = ?", (module_id,))
            row = cur.fetchone()
            conn.close()
            return row
        except Exception as e:
            logger.exception(f"get_exam_config_for_module Fehler: {e}")
            return None

    def save_exam_config(self, module_id: int, pool_order_str: str) -> bool:
        try:
            conn, cur = self._connect()
            # INSERT OR REPLACE: wir ersetzen die Konfiguration für das Modul
            cur.execute("""
                INSERT INTO exam_configs (module_id, pool_order)
                VALUES (?, ?)
                ON CONFLICT(module_id) DO UPDATE SET pool_order = excluded.pool_order
            """, (module_id, pool_order_str))
            conn.commit()
            conn.close()
            logger.info(f"Klausurkonfiguration für Modul ID {module_id} gespeichert.")
            return True
        except Exception as e:
            logger.exception(f"save_exam_config Fehler: {e}")
            return False

    def close(self):
        # Da wir pro-Operation Verbindungen öffnen und sofort schließen,
        # gibt es hier nichts Großes zu schließen. Wir geben nur Info.
        logger.info("DatabaseManager: keine persistenten Verbindungen zu schließen (per-op connections used).")
