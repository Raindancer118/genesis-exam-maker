# main.py
import logging
import shutil
from tkinter import messagebox
from gui.main_window import KlausurApp
from gui.splash_screen import SplashScreen
from core.logger_config import setup_logging
from core.database_manager import DatabaseManager
from core.latex_generator import run_test_compilation


def run_startup_checks(splash, db_manager):  # Nimmt jetzt den db_manager entgegen
    """Führt die System-Checks mit der übergebenen DB-Verbindung aus."""
    try:
        splash.update_progress(10, "Prüfe Abhängigkeiten...")
        if not shutil.which("lualatex"): raise RuntimeError("LuaLaTeX nicht gefunden.")
        if not shutil.which("pandoc"): raise RuntimeError("Pandoc nicht gefunden.")

        splash.update_progress(40, "Prüfe Datenbank...")
        # Erstellt keine neue Verbindung, sondern nutzt die bestehende
        db_manager.setup_database()

        splash.update_progress(70, "Führe Test-Kompilierung durch...")
        success, message = run_test_compilation()
        if not success: raise RuntimeError(f"Test-Kompilierung fehlgeschlagen: {message}")

        splash.update_progress(100, "Start erfolgreich!")
        return True

    except Exception as e:
        logging.error(f"Fehler beim Start-Check: {e}")
        splash.close()
        messagebox.showerror("Startfehler", f"Ein kritischer Fehler ist aufgetreten:\n\n{e}")
        return False


if __name__ == '__main__':
    setup_logging()

    # 1. ERSTELLE EINE EINZIGE DB-VERBINDUNG FÜR DIE GESAMTE LAUFZEIT
    db = DatabaseManager()

    # 2. Haupt-App erstellen und verstecken, ÜBERGIB die DB-Verbindung
    app = KlausurApp(db)
    app.withdraw()

    # 3. Splash Screen erstellen
    splash = SplashScreen(app)

    # 4. Checks ausführen, ÜBERGIB die DB-Verbindung
    checks_passed = run_startup_checks(splash, db)

    splash.close()

    if checks_passed:
        logging.info("Anwendung wird gestartet...")
        app.deiconify()
        app.mainloop()  # Hier wird on_closing am Ende aufgerufen, was die DB schließt
    else:
        logging.error("Start-Checks fehlgeschlagen. Programmstart abgebrochen.")
        db.close()  # Schließe die DB, wenn die App nie startet