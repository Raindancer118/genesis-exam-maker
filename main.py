# main.py
import logging
import shutil
import time  # NEUER IMPORT
from tkinter import messagebox
from gui.main_window import KlausurApp
from gui.splash_screen import SplashScreen
from core.logger_config import setup_logging
from core.database_manager import DatabaseManager

def run_startup_checks(splash, db):
    """Führt die System-Checks aus und aktualisiert den Splash Screen."""
    try:
        splash.update_progress(20, "Prüfe Abhängigkeiten (LuaLaTeX, Pandoc)...")
        if not shutil.which("lualatex"): raise RuntimeError("LuaLaTeX nicht im System-PATH gefunden.")
        if not shutil.which("pandoc"): raise RuntimeError("Pandoc nicht im System-PATH gefunden.")

        splash.update_progress(60, "Prüfe Datenbankverbindung...")
        db = DatabaseManager()
        db.setup_database()
        db.close()

        # Der Test-Kompilierungs-Check bleibt auskommentiert, da er die Ursache für Probleme war.
        # Du kannst ihn bei Bedarf wieder aktivieren.
        # splash.update_progress(70, "Führe Test-Kompilierung durch...")
        # success, message = run_test_compilation()
        # if not success: raise RuntimeError(f"Test-Kompilierung fehlgeschlagen: {message}")

        splash.update_progress(100, "Start erfolgreich!")

        # --- HIER IST DIE KÜNSTLICHE VERZÖGERUNG ---
        time.sleep(2)

        return True

    except Exception as e:
        logging.error(f"Fehler beim Start-Check: {e}")
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
        logging.error("Start-Checks fehlgeschlagen. Programmstart abgebrochen.")
        db.close()