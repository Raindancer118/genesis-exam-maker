# main.py (relevante Ergänzungen am Ende)
import webview
from pathlib import Path
import threading
import time
import shutil
import subprocess
import sys
import pypandoc
from core.database_manager import DatabaseManager
from core.exam_builder import ExamBuilder  # oben importieren


# main.py — ersetze die bisherige Api-Klasse durch diese robuste Version
import logging
from core.database_manager import DatabaseManager
from core.exam_builder import ExamBuilder

logger = logging.getLogger(__name__)

class Api:
    """
    API class that exposes Python functions to the JavaScript frontend.
    Returns JSON-like dicts for mutating calls so JS can react.
    """
    def __init__(self):
        try:
            self.db = DatabaseManager()
            self.db.setup_database()
            logger.info("DatabaseManager ready.")
        except Exception as e:
            logger.exception("Initialisierungsfehler: Datenbank: %s", e)
            # still set attribute so JS can call and see errors
            self.db = None

    # --- read helpers (return lists / objects) ---
    def get_modules(self):
        try:
            if not self.db: raise RuntimeError("DB not initialized")
            return self.db.get_modules()
        except Exception as e:
            logger.exception("get_modules Fehler: %s", e)
            return []

    def get_module_by_id(self, module_id):
        try:
            if not self.db: raise RuntimeError("DB not initialized")
            return self.db.get_module_by_id(module_id)
        except Exception as e:
            logger.exception("get_module_by_id Fehler: %s", e)
            return None

    def get_pools_for_module(self, module_id):
        try:
            if not self.db: raise RuntimeError("DB not initialized")
            return self.db.get_pools_for_module(module_id)
        except Exception as e:
            logger.exception("get_pools_for_module Fehler: %s", e)
            return []

    def get_pool_with_module_info(self, pool_id):
        try:
            if not self.db: raise RuntimeError("DB not initialized")
            return self.db.get_pool_with_module_info(pool_id)
        except Exception as e:
            logger.exception("get_pool_with_module_info Fehler: %s", e)
            return None

    def get_tasks_from_pool(self, pool_id):
        try:
            if not self.db: raise RuntimeError("DB not initialized")
            tasks_from_db = self.db.get_tasks_from_pool(pool_id)
            processed_tasks = []
            for task_id, raw_md in tasks_from_db:
                try:
                    html_content = pypandoc.convert_text(raw_md, 'html5', format='md')
                    processed_tasks.append({'id': task_id, 'raw_md': raw_md, 'html': html_content})
                except OSError:
                    error_html = "<p><em>Error rendering Markdown. Is Pandoc installed?</em></p>"
                    processed_tasks.append({'id': task_id, 'raw_md': raw_md, 'html': error_html})
            return processed_tasks
        except Exception as e:
            logger.exception("get_tasks_from_pool Fehler: %s", e)
            return []

    # --- create / mutate: return {success, message} ---
    def add_module(self, module_name):
        try:
            if not self.db: raise RuntimeError("DB not initialized")
            res = self.db.add_module(module_name)
            if res:
                return {"success": True, "message": f"Module '{module_name}' added.", "id": res}
            else:
                return {"success": False, "message": f"Module '{module_name}' already exists or error."}
        except Exception as e:
            logger.exception("add_module Fehler: %s", e)
            return {"success": False, "message": str(e)}

    def add_pool(self, pool_name, module_id):
        try:
            if not self.db: raise RuntimeError("DB not initialized")
            res = self.db.add_pool(pool_name, module_id)
            if res:
                return {"success": True, "message": f"Pool '{pool_name}' added.", "id": res}
            return {"success": False, "message": "Could not add pool."}
        except Exception as e:
            logger.exception("add_pool Fehler: %s", e)
            return {"success": False, "message": str(e)}

    def add_task(self, task_content, pool_id):
        try:
            if not self.db: raise RuntimeError("DB not initialized")
            res = self.db.add_task(task_content, pool_id)
            if res:
                return {"success": True, "message": "New task added.", "id": res}
            return {"success": False, "message": "Could not add task."}
        except Exception as e:
            logger.exception("add_task Fehler: %s", e)
            return {"success": False, "message": str(e)}

    def delete_module(self, module_id):
        try:
            if not self.db: raise RuntimeError("DB not initialized")
            ok = self.db.delete_module(module_id)
            if ok:
                return {"success": True, "message": f"Module {module_id} deleted."}
            else:
                return {"success": False, "message": "Delete returned false."}
        except Exception as e:
            logger.exception("delete_module Fehler: %s", e)
            return {"success": False, "message": str(e)}

    def delete_pool(self, pool_id):
        try:
            if not self.db: raise RuntimeError("DB not initialized")
            ok = self.db.delete_pool(pool_id)
            if ok:
                return {"success": True, "message": f"Pool {pool_id} deleted."}
            else:
                return {"success": False, "message": "Delete returned false."}
        except Exception as e:
            logger.exception("delete_pool Fehler: %s", e)
            return {"success": False, "message": str(e)}

    def delete_task(self, task_id):
        try:
            if not self.db: raise RuntimeError("DB not initialized")
            ok = self.db.delete_task(task_id)
            if ok:
                return {"success": True, "message": f"Task {task_id} deleted."}
            else:
                return {"success": False, "message": "Delete returned false."}
        except Exception as e:
            logger.exception("delete_task Fehler: %s", e)
            return {"success": False, "message": str(e)}


def init_worker(window, api):
    """
    Lädt/initialisiert nacheinander alle benötigten Dienste und meldet Fortschritt ans UI.
    window.evaluate_js("window.setProgress(42, 'Message')")
    """
    steps = [
        ("DB-Verbindung prüfen", 10, lambda: api.db.setup_database()),  # quick sanity
        ("Datenbank: Module laden", 15, lambda: api.get_modules()),
        ("Pandoc/PDF prüfen", 25, lambda: check_pandoc()),              # prüft pandoc
        ("LaTeX-Engine warm starten", 20, lambda: warmup_latex()),      # optionaler Warmup
        ("Plugins & Worker starten", 20, lambda: startup_workers(api)),
        ("Fertig - UI wird geladen", 10, lambda: None)
    ]

    progress = 0
    try:
        for name, weight, fn in steps:
            # Update message
            window.evaluate_js(f"window.setProgress({progress}, 'Starte: {escape_js(name)}')")
            # Ausführen (sicher in try)
            try:
                fn()
            except Exception as e:
                # bei Fehler: kurz mitteilen, aber versuchen weiter zu machen
                window.evaluate_js(f"window.setProgress({progress}, 'Fehler bei: {escape_js(name)} — {escape_js(str(e))}')")
                # ggf. loggen
                print("Initialisierungsfehler:", name, e, file=sys.stderr)
            # erhöhe progress
            progress += weight
            if progress > 99:
                progress = 99
            window.evaluate_js(f"window.setProgress({progress}, '... {escape_js(name)} abgeschlossen')")
            # kleine Pause damit der Benutzer den Fortschritt sieht (kann man entfernen)
            time.sleep(0.3)
    finally:
        # Abschließende 100%-Meldung und Wechsel zur Hauptseite
        window.evaluate_js("window.setProgress(100, 'Fertig. Öffne Anwendung...')")
        # warte kurz, damit Animation sichtbar ist
        time.sleep(0.35)
        index_path = (Path(__file__).resolve().parent / 'web' / 'templates' / 'index.html').resolve().as_uri()
        # Variante A: lässt die WebView die URL direkt laden (schnell & sauber)
        window.load_url(index_path)
        # Variante B (wenn du lieber JS die Navigation machen lässt):
        # window.evaluate_js(f"window.finishAndLoad('{index_path}')")


def escape_js(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'").replace("\n","\\n").replace("\r","")

def check_pandoc():
    # Versuche pandoc via shutil / subprocess zu finden; fallback: pypandoc testen
    if shutil.which("pandoc"):
        try:
            r = subprocess.run(["pandoc", "--version"], capture_output=True, text=True, timeout=3)
            return r.returncode == 0
        except Exception:
            return False
    else:
        # try pypandoc import warmup
        try:
            import pypandoc
            pypandoc.get_pandoc_path()  # kann OSError werfen, falls nicht installiert
            # optional: dummy conversion to warm-up:
            try:
                pypandoc.convert_text("hello", "html5", format="md")
            except Exception:
                pass
            return True
        except Exception:
            return False

def warmup_latex():
    # optionaler check für pdflatex / lualatex
    if shutil.which("pdflatex"):
        try:
            subprocess.run(["pdflatex", "--version"], capture_output=True, timeout=3)
            return True
        except Exception:
            return False
    # kein pdflatex verfügbar ist okay — wir geben False zurück
    return False

def startup_workers(api):
    # Starte hier zusätzliche Worker/Threads, z.B. Hintergrund-Task-Scheduler, Prüfroutinen, etc.
    # Beispiel: den Cache mit häufigen Queries füllen (ohne Blockieren)
    def preload():
        try:
            api.get_modules()
            # weitere preload-Operationen...
        except Exception as e:
            print("Preload-Fehler:", e, file=sys.stderr)
    t = threading.Thread(target=preload, daemon=True)
    t.start()
    return True

if __name__ == '__main__':
    api = Api()
    index_path = (Path(__file__).resolve().parent / 'web' / 'templates' / 'index.html').resolve().as_uri()
    loading_path = (Path(__file__).resolve().parent / 'web' / 'templates' / 'loading.html').resolve().as_uri()

    window = webview.create_window('Genesis Exam Maker', loading_path, js_api=api, width=1000, height=700)
    # Start background initialisation thread
    t = threading.Thread(target=init_worker, args=(window, api), daemon=True)
    t.start()

    # debug=True zeigt DevTools (praktisch beim Entwickeln)
    webview.start(debug=False)


    def build_exam_for_module(self, module_id, filename=''):
        """
        Wrapper, der ExamBuilder aufruft und den Pfad zur erzeugten PDF zurückgibt.
        Rückgabe: dict { 'success': bool, 'path': str, 'message': str }
        """
        try:
            pdf_path = self.exam_builder.build_exam_for_module(module_id, filename=filename if filename else None)
            return {"success": True, "path": pdf_path}
        except Exception as e:
            return {"success": False, "message": str(e)}