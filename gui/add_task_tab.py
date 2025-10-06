# gui/add_task_tab.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import logging

logger = logging.getLogger(__name__)


class AddTaskTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding="10")
        self.controller = controller
        self.db_manager = self.controller.db_manager

        self.modules_data = []
        self.pools_data = []
        self.setup_widgets()
        logger.debug("Aufgabe-hinzufügen-Tab initialisiert.")

    def setup_widgets(self):
        ttk.Label(self, text="Modul auswählen:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.module_var = tk.StringVar()
        self.module_combo = ttk.Combobox(self, textvariable=self.module_var, state="readonly")
        self.module_combo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        ttk.Label(self, text="Aufgabenpool auswählen:").grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.pool_var = tk.StringVar()
        self.pool_combo = ttk.Combobox(self, textvariable=self.pool_var, state="readonly")
        self.pool_combo.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        ttk.Label(self, text="Aufgabentext (Markdown):").grid(row=4, column=0, sticky="w", pady=(0, 5))
        self.task_text = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=15)
        self.task_text.grid(row=5, column=0, columnspan=2, sticky="nsew")

        save_button = ttk.Button(self, text="Aufgabe speichern", command=self.save_task)
        save_button.grid(row=6, column=1, sticky="e", pady=(10, 0))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self.module_combo.bind("<<ComboboxSelected>>", self.on_module_selected)
        self.update_module_dropdown()

    def update_module_dropdown(self):
        logger.debug("Modul-Dropdown wird aktualisiert.")
        self.modules_data = self.db_manager.get_modules()
        module_names = [name for id, name in self.modules_data]
        self.module_combo['values'] = module_names
        self.pool_combo['values'] = []
        self.pool_var.set('')

    def on_module_selected(self, event=None):
        selected_module_name = self.module_var.get()
        logger.debug(f"Modul '{selected_module_name}' ausgewählt. Lade zugehörige Pools.")
        selected_module_id = self.controller.get_id_from_name(self.modules_data, selected_module_name)
        if selected_module_id:
            self.pools_data = self.db_manager.get_pools_for_module(selected_module_id)
            pool_names = [name for id, name in self.pools_data]
            self.pool_combo['values'] = pool_names
            self.pool_var.set('')

    def save_task(self):
        pool_name = self.pool_var.get()
        content = self.task_text.get("1.0", tk.END).strip()
        if not self.module_var.get() or not pool_name or not content:
            messagebox.showerror("Eingabe fehlt", "Bitte alles ausfüllen.")
            return
        selected_pool_id = self.controller.get_id_from_name(self.pools_data, pool_name)
        if selected_pool_id:
            logger.info(f"Speichere neue Aufgabe im Pool '{pool_name}' (ID: {selected_pool_id}).")
            self.db_manager.add_task(content, selected_pool_id)
            messagebox.showinfo("Erfolg", f"Aufgabe wurde zu '{pool_name}' hinzugefügt.")
            self.task_text.delete("1.0", tk.END)
        else:
            logger.error(f"Konnte ID für Pool-Namen '{pool_name}' nicht finden.")
            messagebox.showerror("Fehler", "Pool nicht gefunden.")