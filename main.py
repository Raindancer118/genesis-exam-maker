# main.py
import logging
import shutil
import time
from tkinter import messagebox
from gui.main_window import KlausurApp
from gui.splash_screen import SplashScreen
from core.logger_config import setup_logging
from core.database_manager import DatabaseManager

# HIER IST DIE KORREKTUR: Logger für diese Datei definieren
logger = logging.getLogger(__name__)


def run_startup_checks(splash, db_manager):
    """Führt die System-Checks aus und aktualisiert den Splash Screen."""
    try:
        splash.update_progress(20, "Prüfe Abhängigkeiten (LuaLaTeX, Pandoc)...")
        time.sleep(0.5)
        if not shutil.which("lualatex"): raise RuntimeError("LuaLaTeX nicht im System-PATH gefunden.")
        if not shutil.which("pandoc"): raise RuntimeError("Pandoc nicht im System-PATH gefunden.")

        splash.update_progress(60, "Prüfe Datenbankverbindung...")
        time.sleep(0.5)
        db_manager.setup_database()

        splash.update_progress(80, "Lade Komponenten...")
        time.sleep(0.5)
        splash.update_progress(83, "Lade Komponenten...")
        time.sleep(0.8)
        splash.update_progress(90, "Lade Komponenten...")
        time.sleep(0.9)
        splash.update_progress(100, "Fertig! Starte...")

        return True

    except Exception as e:
        logger.error(f"Fehler beim Start-Check: {e}")
        splash.close()
        messagebox.showerror("Startfehler",
                             f"Ein kritischer Fehler ist aufgetreten:\n\n{e}\n\nDas Programm wird beendet.")
        return False


if __name__ == '__main__':
    setup_logging()

    db = DatabaseManager()
    app = KlausurApp(db)
    app.withdraw()

    splash = SplashScreen(app)

    checks_passed = run_startup_checks(splash, db)

    splash.close()

    if checks_passed:
        logging.info("Anwendung wird gestartet...")
        app.deiconify()
        app.mainloop()
    else:
        logger.error("Start-Checks fehlgeschlagen. Programmstart abgebrochen.")
        db.close()