# gui/generate_exam_tab.py
import tkinter as tk
from tkinter import ttk, Listbox, messagebox
import logging
from core.exam_builder import ExamBuilder

logger = logging.getLogger(__name__)


class GenerateExamTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding="10")
        self.controller = controller
        self.db_manager = self.controller.db_manager

        # Der ExamBuilder wird erst bei Bedarf initialisiert
        self.exam_builder = None

        self.modules_data = []
        self.pools_data = []
        self.setup_widgets()

    def setup_widgets(self):
        # --- Layout-Frames ---
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", pady=(0, 10))

        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill="both")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)  # Spalten für Listboxen
        main_frame.grid_rowconfigure(0, weight=1)

        # --- Top Frame: Modulauswahl ---
        ttk.Label(top_frame, text="Modul für die Klausur auswählen:").pack(anchor="w")
        self.module_var = tk.StringVar()
        self.module_combo = ttk.Combobox(top_frame, textvariable=self.module_var, state="readonly")
        self.module_combo.pack(fill="x")
        self.module_combo.bind("<<ComboboxSelected>>", self.on_module_selected)

        # --- Main Frame: Konfiguration ---
        # Verfügbare Pools (links)
        available_pools_frame = ttk.LabelFrame(main_frame, text="Verfügbare Pools", padding=5)
        available_pools_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.available_pools_listbox = Listbox(available_pools_frame)
        self.available_pools_listbox.pack(expand=True, fill="both")

        # Buttons (mitte)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=1, padx=5)
        add_button = ttk.Button(button_frame, text=">", command=self.add_pool_to_exam)
        add_button.pack(pady=5)
        remove_button = ttk.Button(button_frame, text="X", command=self.remove_pool_from_exam)
        remove_button.pack(pady=5)

        # Klausurstruktur (rechts)
        exam_structure_frame = ttk.LabelFrame(main_frame, text="Klausur-Struktur", padding=5)
        exam_structure_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        self.exam_pools_listbox = Listbox(exam_structure_frame)
        self.exam_pools_listbox.pack(expand=True, fill="both")

        # --- Bottom Frame: Aktionen ---
        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x", pady=(10, 0))
        self.save_config_button = ttk.Button(action_frame, text="Konfiguration speichern",
                                             command=self.save_configuration)
        self.save_config_button.pack(side="left")
        self.generate_button = ttk.Button(action_frame, text="Klausur generieren!", command=self.generate_exam)
        self.generate_button.pack(side="right")

    def update_module_dropdown(self):
        """Wird vom Controller aufgerufen."""
        logger.debug("GenerateTab: Modul-Dropdown wird aktualisiert.")
        self.modules_data = self.db_manager.get_modules()
        self.module_combo['values'] = [name for id, name in self.modules_data]
        self.clear_lists()

    def on_module_selected(self, event=None):
        self.clear_lists()
        selected_module_name = self.module_var.get()
        if not selected_module_name: return

        module_id = self.controller.get_id_from_name(self.modules_data, selected_module_name)
        if not module_id: return

        logger.info(f"GenerateTab: Modul '{selected_module_name}' (ID: {module_id}) ausgewählt.")
        # Lade verfügbare Pools
        self.pools_data = self.db_manager.get_pools_for_module(module_id)
        for pool_id, name in self.pools_data:
            self.available_pools_listbox.insert(tk.END, f"{pool_id}: {name}")

        # Lade gespeicherte Konfiguration, falls vorhanden
        config = self.db_manager.get_exam_config_for_module(module_id)
        if config:
            pool_order_ids = config[2].split(',')
            # Erstelle ein Dictionary für schnellen Zugriff auf Pool-Namen
            pool_dict = {str(p_id): p_name for p_id, p_name in self.pools_data}
            for p_id in pool_order_ids:
                if p_id in pool_dict:
                    self.exam_pools_listbox.insert(tk.END, f"{p_id}: {pool_dict[p_id]}")

    def add_pool_to_exam(self):
        selection = self.available_pools_listbox.curselection()
        if not selection: return

        selected_item = self.available_pools_listbox.get(selection[0])
        self.exam_pools_listbox.insert(tk.END, selected_item)
        logger.debug(f"'{selected_item}' zur Klausurstruktur hinzugefügt.")

    def remove_pool_from_exam(self):
        selection = self.exam_pools_listbox.curselection()
        if not selection: return

        logger.debug(f"'{self.exam_pools_listbox.get(selection[0])}' aus Klausurstruktur entfernt.")
        self.exam_pools_listbox.delete(selection[0])

    def save_configuration(self):
        selected_module_name = self.module_var.get()
        if not selected_module_name:
            messagebox.showerror("Fehler", "Bitte zuerst ein Modul auswählen.");
            return

        module_id = self.controller.get_id_from_name(self.modules_data, selected_module_name)
        if not module_id: return

        # Erstelle den String der Pool-IDs
        pool_items = self.exam_pools_listbox.get(0, tk.END)
        if not pool_items:
            messagebox.showwarning("Leere Konfiguration",
                                   "Die Klausur-Struktur ist leer. Es wird eine leere Konfiguration gespeichert.");

        pool_ids = [item.split(":")[0] for item in pool_items]
        pool_order_str = ",".join(pool_ids)

        self.db_manager.save_exam_config(module_id, pool_order_str)
        messagebox.showinfo("Gespeichert",
                            f"Die Konfiguration für '{selected_module_name}' wurde erfolgreich gespeichert.")

    def generate_exam(self):
        selected_module_name = self.module_var.get()
        if not selected_module_name:
            messagebox.showerror("Fehler", "Bitte zuerst ein Modul auswählen.");
            return

        module_id = self.controller.get_id_from_name(self.modules_data, selected_module_name)
        if not module_id: return

        # Prüfe, ob eine Konfiguration existiert
        if self.exam_pools_listbox.size() == 0:
            messagebox.showerror("Fehler",
                                 "Die Klausur-Struktur ist leer. Bitte füge Pools hinzu und speichere die Konfiguration.")
            return

        logger.info(f"Starte Klausur-Generierung für Modul '{selected_module_name}'...")
        if not self.exam_builder:
            self.exam_builder = ExamBuilder(self.db_manager)

        # Führe die eigentliche Generierung aus
        success, message = self.exam_builder.build_exam_for_module(module_id)

        if success:
            messagebox.showinfo("Erfolg", message)
        else:
            messagebox.showerror("Fehler bei der Generierung", message)

    def clear_lists(self):
        self.available_pools_listbox.delete(0, tk.END)
        self.exam_pools_listbox.delete(0, tk.END)