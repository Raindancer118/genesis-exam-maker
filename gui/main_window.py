# gui/main_window.py
import tkinter as tk
from tkinter import ttk
import logging
from core.database_manager import DatabaseManager

# Importiere die neuen Tab-Klassen
from .add_task_tab import AddTaskTab
from .management_tab import ManagementTab

logger = logging.getLogger(__name__)


class KlausurApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Klausur-Generator")
        self.geometry("1200x700")

        self.db_manager = DatabaseManager()
        self.setup_ui()

    def setup_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(pady=10, padx=10, expand=True, fill="both")

        # Erstelle Instanzen der Tab-Klassen
        self.task_tab = AddTaskTab(notebook, self)
        self.manage_tab = ManagementTab(notebook, self)
        # Platzhalter für den dritten Tab
        generate_tab_placeholder = ttk.Frame(notebook)

        notebook.add(self.task_tab, text="Aufgabe hinzufügen")
        notebook.add(self.manage_tab, text="Verwaltung")
        notebook.add(generate_tab_placeholder, text="Klausur generieren")

        logger.debug("UI-Setup abgeschlossen, alle Tabs initialisiert.")

        # HIER IST DIE KORREKTUR:
        # Nachdem die gesamte UI aufgebaut ist, stoßen wir das initiale Laden der Daten an.
        self.on_modules_changed()

    def on_modules_changed(self):
        """Zentrale Methode, um alle relevanten UI-Teile zu aktualisieren."""
        logger.info("Moduldaten haben sich geändert, aktualisiere abhängige UI-Komponenten...")
        self.task_tab.update_module_dropdown()
        self.manage_tab.update_module_listbox()

    def get_id_from_name(self, data_list, name_to_find):
        """Allgemeine Hilfsfunktion, die von den Tabs genutzt werden kann."""
        if not data_list: return None
        for id, name in data_list:
            if name == name_to_find:
                return id
        return None

    def on_closing(self):
        logger.info("Schließungs-Protokoll aufgerufen.")
        self.db_manager.close()
        self.destroy()