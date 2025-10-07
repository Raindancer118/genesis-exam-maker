# gui/import_export_tab.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Toplevel, simpledialog
import logging
from core.import_export_manager import import_data, export_data

logger = logging.getLogger(__name__)


class ImportExportTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding="10")
        self.controller = controller
        self.db_manager = self.controller.db_manager
        self.modules_data = []
        self.pools_data = []

        self.setup_widgets()

    def setup_widgets(self):
        # --- Export-Bereich ---
        export_frame = ttk.LabelFrame(self, text="Exportieren", padding="10")
        export_frame.pack(fill="x", pady=(0, 20))

        ttk.Label(export_frame, text="Modul auswählen:").grid(row=0, column=0, sticky="w")
        self.module_var = tk.StringVar()
        self.module_combo = ttk.Combobox(export_frame, textvariable=self.module_var, state="readonly")
        self.module_combo.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self.module_combo.bind("<<ComboboxSelected>>", self.on_module_selected)

        ttk.Label(export_frame, text="Pool auswählen (optional):").grid(row=0, column=1, sticky="w")
        self.pool_var = tk.StringVar()
        self.pool_combo = ttk.Combobox(export_frame, textvariable=self.pool_var, state="readonly")
        self.pool_combo.grid(row=1, column=1, sticky="ew")

        export_button = ttk.Button(export_frame, text="Daten exportieren...", command=self.handle_export)
        export_button.grid(row=2, column=0, columnspan=2, sticky="e", pady=(10, 0))
        export_frame.grid_columnconfigure(0, weight=1)
        export_frame.grid_columnconfigure(1, weight=1)

        # --- Import-Bereich ---
        import_frame = ttk.LabelFrame(self, text="Importieren", padding="10")
        import_frame.pack(fill="x")

        ttk.Label(import_frame, text="Wähle eine .geex-Datei zum Importieren aus.").pack(anchor="w", pady=5)
        import_button = ttk.Button(import_frame, text="Datei importieren...", command=self.handle_import)
        import_button.pack(anchor="e", pady=5)

    def update_module_dropdown(self):
        self.modules_data = self.db_manager.get_modules()
        self.module_combo['values'] = [name for id, name in self.modules_data]
        self.clear_pool_dropdown()

    def on_module_selected(self, event=None):
        self.clear_pool_dropdown()
        selected_module_name = self.module_var.get()
        module_id = self.controller.get_id_from_name(self.modules_data, selected_module_name)
        if module_id:
            self.pools_data = self.db_manager.get_pools_for_module(module_id)
            # "Alle Pools" als erste Option hinzufügen
            pool_names = ["[ Alle Pools des Moduls ]"] + [name for id, name in self.pools_data]
            self.pool_combo['values'] = pool_names
            self.pool_var.set(pool_names[0])

    def handle_export(self):
        selected_module_name = self.module_var.get()
        if not selected_module_name:
            messagebox.showerror("Fehler", "Bitte wähle zuerst ein Modul aus.")
            return

        module_id = self.controller.get_id_from_name(self.modules_data, selected_module_name)

        selected_pool_name = self.pool_var.get()
        pool_id = None
        if selected_pool_name and selected_pool_name != "[ Alle Pools des Moduls ]":
            pool_id = self.controller.get_id_from_name(self.pools_data, selected_pool_name)

        file_path = filedialog.asksaveasfilename(
            defaultextension=".geex",
            filetypes=[("Genesis Exam Maker Export", "*.geex"), ("Alle Dateien", "*.*")]
        )
        if not file_path: return

        success, message = export_data(self.db_manager, file_path, module_id, pool_id)
        if success:
            messagebox.showinfo("Export erfolgreich", message)
        else:
            messagebox.showerror("Export fehlgeschlagen", message)

    def handle_import(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Genesis Exam Maker Export", "*.geex"), ("Alle Dateien", "*.*")]
        )
        if not file_path: return

        def ask_on_conflict(task_content):
            """Diese Funktion wird vom Importer aufgerufen, wenn ein Duplikat gefunden wird."""
            # Einfacher Dialog als Beispiel. Kann erweitert werden.
            # TRUE = skip, FALSE = cancel
            user_choice = messagebox.askyesnocancel(
                "Konflikt gefunden",
                "Eine Aufgabe mit dem folgenden Inhalt existiert bereits:\n\n"
                f"{task_content[:200]}...\n\n"
                "Möchtest du diese Aufgabe überspringen (Ja) oder den gesamten Import abbrechen (Nein)?",
                icon='warning'
            )
            if user_choice is None: return "cancel"
            return "skip" if user_choice else "cancel"

        success, message = import_data(self.db_manager, file_path, ask_on_conflict)
        if success:
            messagebox.showinfo("Import abgeschlossen", message)
            # Wichtig: UI aktualisieren, da neue Daten vorhanden sind
            self.controller.on_modules_changed()
        else:
            messagebox.showerror("Import fehlgeschlagen", message)

    def clear_pool_dropdown(self):
        self.pool_combo['values'] = [];
        self.pool_var.set('')