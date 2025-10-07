# main.py
import shutil
import os
import logging
from gui.main_window import KlausurApp
from core.logger_config import setup_logging


if __name__ == '__main__':
    setup_logging()

    logging.info("Anwendung wird gestartet...")
    app = KlausurApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
    logging.info("Anwendung wurde beendet.")