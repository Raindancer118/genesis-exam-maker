# core/logger_config.py
import logging
import sys


def setup_logging():
    """Konfiguriert das zentrale Logging für die gesamte Anwendung."""
    # Definiere das Format für die Log-Nachrichten
    log_format = logging.Formatter(
        '%(asctime)s - %(levelname)-8s - %(name)-28s - %(message)s'
    )

    # Erstelle einen Handler für die Ausgabe in der Konsole (ab Level INFO)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)

    # Erstelle einen Handler für die Ausgabe in eine Datei (ab Level DEBUG)
    file_handler = logging.FileHandler("app.log", mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)

    # Hole den Root-Logger, setze das niedrigste Level und füge die Handler hinzu
    root_logger = logging.getLogger()
    # Verhindert doppelte Logs, falls die Funktion mehrfach aufgerufen wird
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)