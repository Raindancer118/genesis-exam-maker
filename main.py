# main.py
import logging
from gui.main_window import KlausurApp
from core.logger_config import setup_logging

if __name__ == '__main__':
    # Logging für die gesamte Anwendung ganz am Anfang konfigurieren
    setup_logging()

    logging.info("Anwendung wird gestartet...")
    app = KlausurApp()
    # Stellt sicher, dass die DB-Verbindung beim Schließen des Fensters beendet wird
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
    logging.info("Anwendung wurde beendet.")