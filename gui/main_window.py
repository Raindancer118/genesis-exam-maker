# gui/main_window.py
import tkinter as tk
from tkinter import ttk
from core.database_manager import DatabaseManager

# Importiere die neuen Tab-Klassen
from .add_task_tab import AddTaskTab
from .management_tab import ManagementTab

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

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_modules_changed(self):
        """Zentrale Methode, um alle relevanten UI-Teile zu aktualisieren."""
        print("Controller: Module haben sich geändert, aktualisiere alle Tabs...")
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
        self.db_manager.close()
        self.destroy()