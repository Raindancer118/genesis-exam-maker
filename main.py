# main.py
import os
import sys
import time
import shutil
import subprocess
import threading
from pathlib import Path

import webview
import pypandoc

import logging

from core.database_manager import DatabaseManager
from core.exam_builder import ExamBuilder

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def get_default_db_path() -> str:
    """Sicheren absoluten Pfad zur Datenbank zurückgeben."""
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return str((data_dir / "klausur.db").resolve())


class Api:
    """
    API class that exposes Python functions to the JavaScript frontend.
    Uses a db_path stored on the Api instance and opens short-lived DatabaseManager instances
    for each call to avoid SQLite thread-safety issues.
    """

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or get_default_db_path()
        # try to ensure DB/tables exist (best-effort)
        try:
            db = DatabaseManager(self.db_path)
            db.setup_database()
            db.close()
            logger.info("Datenbank initialisiert unter %s", self.db_path)
        except Exception as e:
            logger.exception("Initialisierungsfehler beim Setup der Datenbank: %s", e)
            # keep object available so frontend sees structured errors

    # --- helper to get a fresh db manager for each call ---
    def _get_db(self) -> DatabaseManager:
        return DatabaseManager(self.db_path)

    # --- READ helpers ---
    def get_modules(self):
        try:
            db = self._get_db()
            rows = db.get_modules()
            db.close()
            return rows or []
        except Exception as e:
            logger.exception("get_modules Fehler: %s", e)
            return []

    def get_module_by_id(self, module_id):
        try:
            db = self._get_db()
            row = db.get_module_by_id(module_id)
            db.close()
            return row
        except Exception as e:
            logger.exception("get_module_by_id Fehler: %s", e)
            return None

    def get_pools_for_module(self, module_id):
        try:
            db = self._get_db()
            rows = db.get_pools_for_module(module_id)
            db.close()
            return rows or []
        except Exception as e:
            logger.exception("get_pools_for_module Fehler: %s", e)
            return []

    def get_pool_with_module_info(self, pool_id):
        try:
            db = self._get_db()
            row = db.get_pool_with_module_info(pool_id)
            db.close()
            return row
        except Exception as e:
            logger.exception("get_pool_with_module_info Fehler: %s", e)
            return None

    def get_tasks_from_pool(self, pool_id):
        try:
            db = self._get_db()
            tasks_from_db = db.get_tasks_from_pool(pool_id)
            db.close()
            processed_tasks = []
            for task_id, raw_md in tasks_from_db:
                try:
                    html_content = pypandoc.convert_text(raw_md, "html5", format="md")
                    processed_tasks.append({"id": task_id, "raw_md": raw_md, "html": html_content})
                except OSError:
                    error_html = "<p><em>Error rendering Markdown. Is Pandoc installed?</em></p>"
                    processed_tasks.append({"id": task_id, "raw_md": raw_md, "html": error_html})
            return processed_tasks
        except Exception as e:
            logger.exception("get_tasks_from_pool Fehler: %s", e)
            return []

    # --- MUTATE helpers (return dicts for JS) ---
    def add_module(self, module_name: str):
        try:
            if not module_name or not str(module_name).strip():
                return {"success": False, "message": "Module name cannot be empty."}
            db = self._get_db()
            last_id = db.add_module(module_name)
            db.close()
            if last_id:
                return {"success": True, "message": f"Module '{module_name}' added.", "id": last_id}
            return {"success": False, "message": f"Module '{module_name}' already exists."}
        except Exception as e:
            logger.exception("add_module Fehler: %s", e)
            return {"success": False, "message": str(e)}

    def add_pool(self, pool_name: str, module_id: int):
        try:
            if not pool_name or not str(pool_name).strip():
                return {"success": False, "message": "Pool name cannot be empty."}
            db = self._get_db()
            last_id = db.add_pool(pool_name, module_id)
            db.close()
            if last_id:
                return {"success": True, "message": f"Pool '{pool_name}' added.", "id": last_id}
            return {"success": False, "message": "Could not add pool."}
        except Exception as e:
            logger.exception("add_pool Fehler: %s", e)
            return {"success": False, "message": str(e)}

    def add_task(self, task_content: str, pool_id: int):
        try:
            if not task_content or not str(task_content).strip():
                return {"success": False, "message": "Task content cannot be empty."}
            db = self._get_db()
            last_id = db.add_task(task_content, pool_id)
            db.close()
            if last_id:
                return {"success": True, "message": "New task added.", "id": last_id}
            return {"success": False, "message": "Could not add task."}
        except Exception as e:
            logger.exception("add_task Fehler: %s", e)
            return {"success": False, "message": str(e)}

    def delete_module(self, module_id: int):
        try:
            db = self._get_db()
            res = db.delete_module(module_id)
            db.close()
            return {"success": True, "message": f"Module {module_id} deleted."}
        except Exception as e:
            logger.exception("delete_module Fehler: %s", e)
            return {"success": False, "message": str(e)}

    def delete_pool(self, pool_id: int):
        try:
            db = self._get_db()
            res = db.delete_pool(pool_id)
            db.close()
            return {"success": True, "message": f"Pool {pool_id} deleted."}
        except Exception as e:
            logger.exception("delete_pool Fehler: %s", e)
            return {"success": False, "message": str(e)}

    def delete_task(self, task_id: int):
        try:
            db = self._get_db()
            res = db.delete_task(task_id)
            db.close()
            return {"success": True, "message": f"Task {task_id} deleted."}
        except Exception as e:
            logger.exception("delete_task Fehler: %s", e)
            return {"success": False, "message": str(e)}

    def update_task(self, task_id: int, new_content: str):
        try:
            db = self._get_db()
            db.update_task(task_id, new_content)
            db.close()
            return {"success": True, "message": "Aufgabe aktualisiert."}
        except Exception as e:
            logger.exception("update_task Fehler: %s", e)
            return {"success": False, "message": str(e)}

    # --- Exam generation wrapper ---
    def build_exam_for_module(self, module_id: int, filename: str = ""):
        """
        Wrapper that uses ExamBuilder to generate the exam PDF.
        Returns a dict suitable for JS consumption.
        """
        try:
            db = self._get_db()
            builder = ExamBuilder(db)  # ExamBuilder should accept a DatabaseManager instance
            # builder may use db and close it itself or not; to be safe we do not close db until after build
            pdf_path = builder.build_exam_for_module(module_id, filename=filename or None)
            # ensure closing DB after builder finished
            try:
                db.close()
            except Exception:
                pass
            return {"success": True, "path": pdf_path}
        except Exception as e:
            logger.exception("build_exam_for_module Fehler: %s", e)
            return {"success": False, "message": str(e)}


# --- Initialization worker / helpers (UI loading splash) --- #
def escape_js(s: str) -> str:
    return str(s).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")


def check_pandoc() -> bool:
    if shutil.which("pandoc"):
        try:
            r = subprocess.run(["pandoc", "--version"], capture_output=True, text=True, timeout=3)
            return r.returncode == 0
        except Exception:
            return False
    else:
        try:
            import pypandoc as _p
            _p.get_pandoc_path()
            try:
                _p.convert_text("hello", "html5", format="md")
            except Exception:
                pass
            return True
        except Exception:
            return False


def warmup_latex() -> bool:
    if shutil.which("pdflatex"):
        try:
            subprocess.run(["pdflatex", "--version"], capture_output=True, timeout=3)
            return True
        except Exception:
            return False
    return False


def startup_workers(api: Api):
    def preload():
        try:
            # use api methods (they open their own DB connections)
            api.get_modules()
        except Exception as e:
            logger.exception("Preload-Fehler: %s", e)
    t = threading.Thread(target=preload, daemon=True)
    t.start()
    return True


def init_worker(window: webview.Window, api: Api):
    """
    Sequential startup steps reported to the web UI via window.evaluate_js.
    Uses short-lived DB connections (no long-lived db on Api required).
    """
    steps = [
        ("DB: Tabellen prüfen & anlegen", 10, lambda: DatabaseManager(get_default_db_path()).setup_database()),
        ("Datenbank: Module laden", 20, lambda: api.get_modules()),
        ("Pandoc/PDF prüfen", 25, lambda: check_pandoc()),
        ("LaTeX-Engine warm starten", 20, lambda: warmup_latex()),
        ("Plugins & Worker starten", 20, lambda: startup_workers(api)),
        ("Fertig - UI wird geladen", 5, lambda: None),
    ]

    progress = 0
    try:
        for name, weight, fn in steps:
            try:
                window.evaluate_js(f"window.setProgress({progress}, 'Starte: {escape_js(name)}')")
            except Exception:
                # if evaluate_js fails (window not ready), just continue; UI will poll later
                logger.debug("Konnte progress nicht per evaluate_js senden (Window noch nicht bereit).")
            # execute
            try:
                fn()
            except Exception as e:
                try:
                    window.evaluate_js(f"window.setProgress({progress}, 'Fehler: {escape_js(name)} — {escape_js(str(e))}')")
                except Exception:
                    pass
                logger.exception("Fehler beim Step '%s': %s", name, e)
            progress += weight
            if progress > 99:
                progress = 99
            try:
                window.evaluate_js(f"window.setProgress({progress}, '... {escape_js(name)} abgeschlossen')")
            except Exception:
                pass
            time.sleep(0.25)
    finally:
        try:
            window.evaluate_js("window.setProgress(100, 'Fertig. Öffne Anwendung...')")
        except Exception:
            pass
        time.sleep(0.25)
        index_path = (Path(__file__).resolve().parent / "web" / "templates" / "index.html").resolve().as_uri()
        try:
            window.load_url(index_path)
        except Exception:
            # fallback: try instructing page to navigate via JS
            try:
                window.evaluate_js(f"window.finishAndLoad && window.finishAndLoad('{index_path}')")
            except Exception:
                logger.exception("Konnte Index nicht laden.")


if __name__ == "__main__":
    api = Api()
    base = Path(__file__).resolve().parent
    loading_path = (base / "web" / "templates" / "loading.html").resolve().as_uri()
    # create window with loading page, then init_worker will swap to index.html
    window = webview.create_window("Genesis Exam Maker", loading_path, js_api=api, width=1000, height=700)

    # start init worker in background
    t = threading.Thread(target=init_worker, args=(window, api), daemon=True)
    t.start()

    # start webview loop
    webview.start(debug=False)
