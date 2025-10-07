# gui/main_window.py
import tkinter as tk
from tkinter import ttk
import logging
from PIL import Image, ImageTk
from core.database_manager import DatabaseManager
from .add_task_tab import AddTaskTab
from .management_tab import ManagementTab
from .generate_exam_tab import GenerateExamTab
from .import_export_tab import ImportExportTab  # NEUER IMPORT

logger = logging.getLogger(__name__)


class KlausurApp(tk.Tk):
    # ... __init__ bleibt gleich ...
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.title("Genesis Exam Maker")
        # ... Rest von __init__ ...
        self.geometry("1200x700")
        try:
            icon_image = Image.open("assets/genesis-exam-maker.png")
            photo = ImageTk.PhotoImage(icon_image)
            self.wm_iconphoto(False, photo)
        except Exception as e:
            logger.warning(f"Konnte Anwendungs-Icon nicht laden: {e}")
        self.db_manager = db_manager
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.setup_ui()

    def setup_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(pady=10, padx=10, expand=True, fill="both")

        self.task_tab = AddTaskTab(notebook, self)
        self.manage_tab = ManagementTab(notebook, self)
        self.generate_tab = GenerateExamTab(notebook, self)
        self.import_export_tab = ImportExportTab(notebook, self)  # NEUE INSTANZ

        notebook.add(self.task_tab, text="Aufgabe hinzufügen")
        notebook.add(self.manage_tab, text="Verwaltung")
        notebook.add(self.generate_tab, text="Klausur generieren")
        notebook.add(self.import_export_tab, text="Import/Export")  # NEUER TAB

        logger.debug("UI-Setup abgeschlossen, alle Tabs initialisiert.")
        self.on_modules_changed()

    def on_modules_changed(self):
        logger.info("Moduldaten haben sich geändert, aktualisiere UI-Komponenten...")
        self.task_tab.update_module_dropdown()
        self.manage_tab.update_module_listbox()
        self.generate_tab.update_module_dropdown()
        self.import_export_tab.update_module_dropdown()  # NEUE ZEILE

    # ... Rest der Klasse bleibt gleich ...
    def get_id_from_name(self, data_list, name_to_find):
        if not data_list: return None
        for id, name in data_list:
            if name == name_to_find: return id
        return None

    def on_closing(self):
        logger.info("Schließungs-Protokoll aufgerufen.")
        self.db_manager.close()
        self.destroy()