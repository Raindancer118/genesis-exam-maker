# gui/management_tab.py
import tkinter as tk
from tkinter import ttk, Listbox, Menu, messagebox, Toplevel, scrolledtext


class ManagementTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding="10")
        self.controller = controller
        self.db_manager = self.controller.db_manager

        self.setup_widgets()
        self.update_module_listbox()

    def setup_widgets(self):
        # --- Layout und Frames ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=2)
        self.grid_rowconfigure(0, weight=1)
        module_frame = ttk.LabelFrame(self, text="Module", padding="10")
        module_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        pool_frame = ttk.LabelFrame(self, text="Aufgabenpools", padding="10")
        pool_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        task_frame = ttk.LabelFrame(self, text="Aufgaben im Pool", padding="10")
        task_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0))

        # --- Widgets für Spalte 1: Module ---
        self.module_listbox = Listbox(module_frame)
        self.module_listbox.pack(expand=True, fill="both")
        self.new_module_entry = ttk.Entry(module_frame)
        self.new_module_entry.pack(fill="x", pady=(10, 5))
        add_module_button = ttk.Button(module_frame, text="Modul hinzufügen", command=self.add_new_module)
        add_module_button.pack(fill="x")

        # --- Widgets für Spalte 2: Pools ---
        self.pool_listbox = Listbox(pool_frame)
        self.pool_listbox.pack(expand=True, fill="both")

        # NEU: Widgets zum Hinzufügen von Pools
        self.new_pool_entry = ttk.Entry(pool_frame)
        self.new_pool_entry.pack(fill="x", pady=(10, 5))
        add_pool_button = ttk.Button(pool_frame, text="Pool hinzufügen", command=self.add_new_pool)
        add_pool_button.pack(fill="x")

        # --- Widgets für Spalte 3: Aufgaben ---
        self.task_listbox = Listbox(task_frame)
        self.task_listbox.pack(expand=True, fill="both")

        # --- Events ---
        self.module_listbox.bind("<<ListboxSelect>>", self.on_module_select)
        self.pool_listbox.bind("<Double-1>", self.on_pool_double_click)
        self.task_listbox.bind("<Double-1>", self.on_task_double_click)
        self.setup_context_menus()

    def add_new_pool(self):
        """NEU: Fügt einen neuen Pool zum ausgewählten Modul hinzu."""
        # 1. Prüfen, ob ein Modul ausgewählt ist
        module_sel = self.module_listbox.curselection()
        if not module_sel:
            messagebox.showerror("Kein Modul ausgewählt",
                                 "Bitte wähle zuerst links ein Modul aus, zu dem der Pool hinzugefügt werden soll.")
            return

        module_id = int(self.module_listbox.get(module_sel[0]).split(":")[0])

        # 2. Pool-Namen aus dem Eingabefeld holen
        pool_name = self.new_pool_entry.get().strip()
        if not pool_name:
            messagebox.showerror("Eingabe fehlt", "Bitte gib einen Namen für den neuen Pool ein.")
            return

        # 3. In die Datenbank einfügen und UI aktualisieren
        self.db_manager.add_pool(pool_name, module_id)
        messagebox.showinfo("Erfolg", f"Der Pool '{pool_name}' wurde hinzugefügt.")
        self.new_pool_entry.delete(0, tk.END)
        self.on_module_select()  # Lädt die Pool-Liste für das Modul neu

    # --- Restliche Methoden (unverändert) ---
    def setup_context_menus(self):
        self.context_menu = Menu(self, tearoff=0)
        self.module_listbox.bind("<Button-3>", lambda e: self.show_context_menu(e, "module"))
        self.pool_listbox.bind("<Button-3>", lambda e: self.show_context_menu(e, "pool"))
        self.task_listbox.bind("<Button-3>", lambda e: self.show_context_menu(e, "task"))
        self.bind_all("<Button-1>", lambda e: self.context_menu.unpost(), add="+")
        self.bind_all("<Escape>", lambda e: self.context_menu.unpost(), add="+")

    def show_context_menu(self, event, item_type):
        self.context_menu.delete(0, "end")
        if not event.widget.curselection(): return
        if item_type == "module":
            self.context_menu.add_command(label="Modul löschen", command=self.delete_selected_module)
        elif item_type == "pool":
            self.context_menu.add_command(label="Pool löschen", command=self.delete_selected_pool)
        elif item_type == "task":
            self.context_menu.add_command(label="Aufgabe löschen", command=self.delete_selected_task)
        self.context_menu.post(event.x_root, event.y_root)

    def on_task_double_click(self, event=None):
        selection = self.task_listbox.curselection()
        if not selection: return
        task_id = int(self.task_listbox.get(selection[0]).split(":")[0])
        task_data = next((task for task in self.tasks_data if task[0] == task_id), None)
        if not task_data: return
        task_content = task_data[1]
        edit_window = Toplevel(self)
        edit_window.title(f"Aufgabe #{task_id} bearbeiten")
        edit_window.geometry("600x400")
        edit_text = scrolledtext.ScrolledText(edit_window, wrap=tk.WORD, height=15)
        edit_text.pack(expand=True, fill="both", padx=10, pady=10)
        edit_text.insert("1.0", task_content)
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        save_button = ttk.Button(button_frame, text="Speichern",
                                 command=lambda: self.save_edited_task(task_id, edit_text, edit_window))
        save_button.pack(side="right")
        cancel_button = ttk.Button(button_frame, text="Abbrechen", command=edit_window.destroy)
        cancel_button.pack(side="right", padx=(0, 5))

    def save_edited_task(self, task_id, text_widget, window_to_close):
        new_content = text_widget.get("1.0", tk.END).strip()
        if new_content:
            self.db_manager.update_task(task_id, new_content)
            window_to_close.destroy()
            messagebox.showinfo("Gespeichert", "Die Aufgabe wurde aktualisiert.")
            self.on_pool_double_click()
        else:
            messagebox.showwarning("Leere Aufgabe", "Der Aufgabentext darf nicht leer sein.")

    def delete_selected_pool(self):
        sel = self.pool_listbox.curselection()
        if not sel: return
        item = self.pool_listbox.get(sel[0])
        pool_id, pool_name = item.split(":", 1)
        if messagebox.askyesno("Löschen", f"Pool '{pool_name.strip()}' und alle Aufgaben wirklich löschen?"):
            self.db_manager.delete_pool(int(pool_id))
            self.on_module_select()

    def delete_selected_task(self):
        sel = self.task_listbox.curselection()
        if not sel: return
        task_id = int(self.task_listbox.get(sel[0]).split(":")[0])
        if messagebox.askyesno("Löschen", f"Aufgabe (ID: {task_id}) wirklich löschen?"):
            self.db_manager.delete_task(task_id)
            self.on_pool_double_click()

    def update_module_listbox(self):
        self.modules_data = self.db_manager.get_modules()
        self.module_listbox.delete(0, tk.END)
        for mod_id, name in self.modules_data: self.module_listbox.insert(tk.END, f"{mod_id}: {name}")
        self.pool_listbox.delete(0, tk.END)
        self.task_listbox.delete(0, tk.END)

    def on_module_select(self, event=None):
        sel = self.module_listbox.curselection()
        if not sel: return
        module_id = int(self.module_listbox.get(sel[0]).split(":")[0])
        self.pool_listbox.delete(0, tk.END)
        self.task_listbox.delete(0, tk.END)
        self.pools_data = self.db_manager.get_pools_for_module(module_id)
        for pool_id, name in self.pools_data: self.pool_listbox.insert(tk.END, f"{pool_id}: {name}")

    def on_pool_double_click(self, event=None):
        sel = self.pool_listbox.curselection()
        if not sel: return
        pool_id = int(self.pool_listbox.get(sel[0]).split(":")[0])
        self.task_listbox.delete(0, tk.END)
        self.tasks_data = self.db_manager.get_tasks_from_pool(pool_id)
        for task_id, content in self.tasks_data:
            preview = content.replace('\n', ' ').strip()[:80] + "..."
            self.task_listbox.insert(tk.END, f"{task_id}: {preview}")

    def add_new_module(self):
        name = self.new_module_entry.get().strip()
        if not name: return
        if self.db_manager.add_module(name):
            self.new_module_entry.delete(0, tk.END)
            self.controller.on_modules_changed()
        else:
            messagebox.showwarning("Fehler", "Modul existiert bereits.")

    def delete_selected_module(self):
        sel = self.module_listbox.curselection()
        if not sel: return
        item = self.module_listbox.get(sel[0])
        mod_id, mod_name = item.split(":", 1)
        if messagebox.askyesno("Löschen", f"Modul '{mod_name.strip()}' und alle Inhalte wirklich löschen?"):
            self.db_manager.delete_module(int(mod_id))
            self.controller.on_modules_changed()