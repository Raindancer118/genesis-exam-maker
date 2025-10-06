# gui/main_window.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Listbox
from core.database_manager import DatabaseManager


# from core.exam_builder import ExamBuilder # Noch nicht benötigt

class KlausurApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Klausur-Generator")
        self.geometry("900x700")

        self.db_manager = DatabaseManager()
        self.setup_ui()

    def setup_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")

        self.task_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.task_tab, text="Aufgabe hinzufügen")
        self.setup_task_tab()

        self.manage_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.manage_tab, text="Verwaltung")
        self.setup_manage_tab()  # NEUE METHODE WIRD HIER AUFGERUFEN

        self.generate_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.generate_tab, text="Klausur generieren")
        # setup_generate_tab() kommt im nächsten Schritt

    # --- Setup für Tab 1: Aufgabe hinzufügen (unverändert) ---
    def setup_task_tab(self):
        # ... (Dieser Teil bleibt exakt wie im vorherigen Schritt)
        ttk.Label(self.task_tab, text="Modul auswählen:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.module_var_tab1 = tk.StringVar()
        self.module_combo_tab1 = ttk.Combobox(self.task_tab, textvariable=self.module_var_tab1, state="readonly")
        self.module_combo_tab1.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Label(self.task_tab, text="Aufgabenpool auswählen:").grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.pool_var_tab1 = tk.StringVar()
        self.pool_combo_tab1 = ttk.Combobox(self.task_tab, textvariable=self.pool_var_tab1, state="readonly")
        self.pool_combo_tab1.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Label(self.task_tab, text="Aufgabentext (Markdown):").grid(row=4, column=0, sticky="w", pady=(0, 5))
        self.task_text = scrolledtext.ScrolledText(self.task_tab, wrap=tk.WORD, height=15)
        self.task_text.grid(row=5, column=0, columnspan=2, sticky="nsew")
        save_button = ttk.Button(self.task_tab, text="Aufgabe speichern", command=self.save_task)
        save_button.grid(row=6, column=1, sticky="e", pady=(10, 0))
        self.task_tab.grid_columnconfigure(0, weight=1)
        self.task_tab.grid_rowconfigure(5, weight=1)
        self.module_combo_tab1.bind("<<ComboboxSelected>>", self.on_module_selected_tab1)
        self.update_module_dropdown_tab1()

    # --- Setup für Tab 2: Verwaltung (NEU) ---
    def setup_manage_tab(self):
        # Container für die zwei Spalten
        module_frame = ttk.LabelFrame(self.manage_tab, text="Module", padding="10")
        module_frame.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        pool_frame = ttk.LabelFrame(self.manage_tab, text="Aufgabenpools", padding="10")
        pool_frame.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")

        self.manage_tab.grid_rowconfigure(0, weight=1)
        self.manage_tab.grid_columnconfigure(0, weight=1)
        self.manage_tab.grid_columnconfigure(1, weight=1)

        # --- Widgets für Modul-Verwaltung (linke Spalte) ---
        self.module_listbox = Listbox(module_frame)
        self.module_listbox.pack(expand=True, fill="both", pady=5)

        self.new_module_entry = ttk.Entry(module_frame)
        self.new_module_entry.pack(fill="x", pady=5)

        add_module_button = ttk.Button(module_frame, text="Neues Modul hinzufügen", command=self.add_new_module)
        add_module_button.pack(fill="x")

        # --- Widgets für Pool-Verwaltung (rechte Spalte) ---
        ttk.Label(pool_frame, text="Modul auswählen:").pack(anchor="w")
        self.module_var_tab2 = tk.StringVar()
        self.module_combo_tab2 = ttk.Combobox(pool_frame, textvariable=self.module_var_tab2, state="readonly")
        self.module_combo_tab2.pack(fill="x", pady=(0, 10))

        self.pool_listbox = Listbox(pool_frame)
        self.pool_listbox.pack(expand=True, fill="both", pady=5)

        self.new_pool_entry = ttk.Entry(pool_frame)
        self.new_pool_entry.pack(fill="x", pady=5)

        add_pool_button = ttk.Button(pool_frame, text="Neuen Pool hinzufügen", command=self.add_new_pool)
        add_pool_button.pack(fill="x")

        # --- Logik und Datenbindung für Tab 2 ---
        self.module_combo_tab2.bind("<<ComboboxSelected>>", self.on_module_selected_tab2)
        self.update_all_module_lists()

    def update_all_module_lists(self):
        """Aktualisiert alle Listen und Dropdowns, die Module anzeigen."""
        self.modules_data = self.db_manager.get_modules()
        module_names = [name for id, name in self.modules_data]

        # Tab 1
        self.module_combo_tab1['values'] = module_names
        # Tab 2
        self.module_listbox.delete(0, tk.END)
        for name in module_names:
            self.module_listbox.insert(tk.END, name)
        self.module_combo_tab2['values'] = module_names

    def add_new_module(self):
        new_module_name = self.new_module_entry.get().strip()
        if not new_module_name:
            messagebox.showerror("Eingabe fehlt", "Bitte einen Namen für das neue Modul eingeben.")
            return

        if self.db_manager.add_module(new_module_name):
            messagebox.showinfo("Erfolg", f"Modul '{new_module_name}' wurde hinzugefügt.")
            self.new_module_entry.delete(0, tk.END)
            self.update_all_module_lists()  # Alle Listen aktualisieren
        else:
            messagebox.showwarning("Fehler", f"Ein Modul mit dem Namen '{new_module_name}' existiert bereits.")

    def on_module_selected_tab2(self, event=None):
        """Aktualisiert die Pool-Liste im Verwaltungs-Tab."""
        self.update_pool_listbox()

    def update_pool_listbox(self):
        selected_module_name = self.module_var_tab2.get()
        selected_module_id = self.get_id_from_name(self.modules_data, selected_module_name)

        self.pool_listbox.delete(0, tk.END)
        if selected_module_id:
            self.pools_data_tab2 = self.db_manager.get_pools_for_module(selected_module_id)
            for id, name in self.pools_data_tab2:
                self.pool_listbox.insert(tk.END, name)

    def add_new_pool(self):
        selected_module_name = self.module_var_tab2.get()
        new_pool_name = self.new_pool_entry.get().strip()

        if not selected_module_name or not new_pool_name:
            messagebox.showerror("Eingabe fehlt",
                                 "Bitte ein Modul auswählen und einen Namen für den neuen Pool eingeben.")
            return

        selected_module_id = self.get_id_from_name(self.modules_data, selected_module_name)
        if selected_module_id:
            self.db_manager.add_pool(new_pool_name, selected_module_id)
            messagebox.showinfo("Erfolg",
                                f"Pool '{new_pool_name}' wurde zum Modul '{selected_module_name}' hinzugefügt.")
            self.new_pool_entry.delete(0, tk.END)
            self.update_pool_listbox()  # Pool-Liste aktualisieren
            # Ggf. auch Pool-Dropdown auf Tab 1 aktualisieren, wenn dasselbe Modul gewählt ist
            if self.module_var_tab1.get() == selected_module_name:
                self.on_module_selected_tab1()

    # --- Hilfsfunktionen & Callbacks für Tab 1 (umbenannt für Klarheit) ---
    def update_module_dropdown_tab1(self):
        self.modules_data = self.db_manager.get_modules()
        module_names = [name for id, name in self.modules_data]
        self.module_combo_tab1['values'] = module_names
        self.pool_combo_tab1['values'] = []
        self.pool_var_tab1.set('')

    def on_module_selected_tab1(self, event=None):
        selected_module_name = self.module_var_tab1.get()
        selected_module_id = self.get_id_from_name(self.modules_data, selected_module_name)
        if selected_module_id:
            self.pools_data_tab1 = self.db_manager.get_pools_for_module(selected_module_id)
            pool_names = [name for id, name in self.pools_data_tab1]
            self.pool_combo_tab1['values'] = pool_names
            self.pool_var_tab1.set('')

    def save_task(self):
        pool_name = self.pool_var_tab1.get()
        content = self.task_text.get("1.0", tk.END).strip()
        if not self.module_var_tab1.get() or not pool_name or not content:
            messagebox.showerror("Eingabe fehlt", "Bitte wähle ein Modul, einen Pool und gib einen Aufgabentext ein.")
            return
        selected_pool_id = self.get_id_from_name(self.pools_data_tab1, pool_name)
        if selected_pool_id:
            self.db_manager.add_task(content, selected_pool_id)
            messagebox.showinfo("Erfolg", f"Aufgabe wurde erfolgreich zum Pool '{pool_name}' hinzugefügt.")
            self.task_text.delete("1.0", tk.END)
        else:
            messagebox.showerror("Fehler", "Konnte den ausgewählten Pool nicht finden.")

    # --- Allgemeine Hilfsfunktion ---
    def get_id_from_name(self, data_list, name_to_find):
        for id, name in data_list:
            if name == name_to_find:
                return id
        return None

    def on_closing(self):
        self.db_manager.close()
        self.destroy()