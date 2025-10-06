# gui/management_tab.py
import tkinter as tk
from tkinter import ttk, Listbox, Menu, messagebox, Toplevel, scrolledtext
import logging

logger = logging.getLogger(__name__)


class ManagementTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding="10")
        self.controller = controller
        self.db_manager = self.controller.db_manager
        self.current_pool_id = None
        self.setup_widgets()

    def setup_widgets(self):
        self.grid_columnconfigure(0, weight=1);
        self.grid_columnconfigure(1, weight=1);
        self.grid_columnconfigure(2, weight=2)
        self.grid_rowconfigure(0, weight=1)
        module_frame = ttk.LabelFrame(self, text="Module", padding="10");
        module_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        pool_frame = ttk.LabelFrame(self, text="Aufgabenpools", padding="10");
        pool_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        task_frame = ttk.LabelFrame(self, text="Aufgaben im Pool", padding="10");
        task_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        self.module_listbox = Listbox(module_frame);
        self.module_listbox.pack(expand=True, fill="both")
        self.new_module_entry = ttk.Entry(module_frame);
        self.new_module_entry.pack(fill="x", pady=(10, 5))
        add_module_button = ttk.Button(module_frame, text="Modul hinzufügen", command=self.add_new_module);
        add_module_button.pack(fill="x")
        self.pool_listbox = Listbox(pool_frame);
        self.pool_listbox.pack(expand=True, fill="both")
        self.new_pool_entry = ttk.Entry(pool_frame);
        self.new_pool_entry.pack(fill="x", pady=(10, 5))
        add_pool_button = ttk.Button(pool_frame, text="Pool hinzufügen", command=self.add_new_pool);
        add_pool_button.pack(fill="x")
        self.task_listbox = Listbox(task_frame);
        self.task_listbox.pack(expand=True, fill="both")
        self.module_listbox.bind("<<ListboxSelect>>", self.on_module_select)
        self.pool_listbox.bind("<Double-1>", self.on_pool_double_click)
        self.task_listbox.bind("<Double-1>", self.on_task_double_click)
        self.setup_context_menus()

    def setup_context_menus(self):
        self.context_menu = Menu(self, tearoff=0)
        self.module_listbox.bind("<Button-3>", lambda e: self.show_context_menu(e, "module"))
        self.pool_listbox.bind("<Button-3>", lambda e: self.show_context_menu(e, "pool"))
        self.task_listbox.bind("<Button-3>", lambda e: self.show_context_menu(e, "task"))

        # HIER IST DIE KORREKTUR: Der störende Linksklick-Befehl wird entfernt.
        # self.bind_all("<Button-1>", lambda e: self.context_menu.unpost(), add="+")
        self.bind_all("<Escape>", lambda e: self.context_menu.unpost(), add="+")

    def show_context_menu(self, event, item_type):
        selection = event.widget.curselection()
        if not selection: return
        selected_index = selection[0]
        selected_item_text = event.widget.get(selected_index)
        item_id, item_name = selected_item_text.split(":", 1)
        item_name = item_name.strip()
        logger.debug(f"Kontextmenü für '{item_type}' (ID: {item_id}) angefordert.")
        self.context_menu.delete(0, "end")
        if item_type == "module":
            self.context_menu.add_command(label=f"Modul '{item_name}' löschen",
                                          command=lambda: self.delete_selected_module(int(item_id), item_name))
        elif item_type == "pool":
            self.context_menu.add_command(label=f"Pool '{item_name}' löschen",
                                          command=lambda: self.delete_selected_pool(int(item_id), item_name))
        elif item_type == "task":
            self.context_menu.add_command(label=f"Aufgabe ID:{item_id} löschen",
                                          command=lambda: self.delete_selected_task(int(item_id)))
        self.context_menu.post(event.x_root, event.y_root)

    def delete_selected_module(self, module_id, module_name):
        logger.debug(f"Bestätigungsdialog für Löschen von Modul ID {module_id} wird angezeigt.")
        if messagebox.askyesno("Löschen bestätigen",
                               f"Möchtest du das Modul '{module_name}' und ALLE zugehörigen Inhalte wirklich löschen?"):
            logger.info(f"Lösche Modul ID {module_id}...");
            self.db_manager.delete_module(module_id);
            self.controller.on_modules_changed()
        else:
            logger.info(f"Löschen von Modul ID {module_id} vom Benutzer abgebrochen.")

    def delete_selected_pool(self, pool_id, pool_name):
        logger.debug(f"Bestätigungsdialog für Löschen von Pool ID {pool_id} wird angezeigt.")
        if messagebox.askyesno("Löschen bestätigen",
                               f"Möchtest du den Pool '{pool_name}' und alle Aufgaben wirklich löschen?"):
            logger.info(f"Lösche Pool ID {pool_id}...");
            self.db_manager.delete_pool(pool_id);
            self.on_module_select()
        else:
            logger.debug(f"Löschen von Pool ID {pool_id} abgebrochen.")

    def delete_selected_task(self, task_id):
        logger.debug(f"Bestätigungsdialog für Löschen von Aufgabe ID {task_id} wird angezeigt.")
        if messagebox.askyesno("Löschen bestätigen",
                               f"Möchtest du die ausgewählte Aufgabe (ID: {task_id}) wirklich löschen?"):
            logger.info(f"Lösche Aufgabe ID {task_id}...");
            self.db_manager.delete_task(task_id);
            self.refresh_task_list()
        else:
            logger.debug(f"Löschen von Aufgabe ID {task_id} abgebrochen.")

    # ... Rest der Methoden bleibt unverändert ...
    def on_pool_double_click(self, event=None):
        sel = self.pool_listbox.curselection();
        if not sel: return;
        pool_id = int(self.pool_listbox.get(sel[0]).split(":")[0]);
        self.current_pool_id = pool_id
        logger.debug(f"Pool ID {pool_id} als aktueller Kontext gesetzt. Lade Aufgaben.");
        self.refresh_task_list()

    def refresh_task_list(self):
        if self.current_pool_id is None: logger.debug("Kein aktueller Pool, Aufgaben-Refresh übersprungen."); return
        logger.debug(f"Aktualisiere Aufgabenliste für Pool ID {self.current_pool_id}.")
        self.task_listbox.delete(0, tk.END)
        self.tasks_data = self.db_manager.get_tasks_from_pool(self.current_pool_id)
        for task_id, content in self.tasks_data: self.task_listbox.insert(tk.END, f"{task_id}: {content.replace(' ', ' ').strip()[:80]}...")

    def on_module_select(self, event=None):
        self.current_pool_id = None;
        sel = self.module_listbox.curselection()
        if not sel: return
        module_id = int(self.module_listbox.get(sel[0]).split(":")[0]);
        logger.debug(f"Modul ID {module_id} ausgewählt. Lade Pools.")
        self.pool_listbox.delete(0, tk.END);
        self.task_listbox.delete(0, tk.END)
        self.pools_data = self.db_manager.get_pools_for_module(module_id)
        for pool_id, name in self.pools_data: self.pool_listbox.insert(tk.END, f"{pool_id}: {name}")

    def add_new_pool(self):
        module_sel = self.module_listbox.curselection()
        if not module_sel: messagebox.showerror("Kein Modul ausgewählt", "Bitte zuerst links ein Modul aus."); return
        module_id = int(self.module_listbox.get(module_sel[0]).split(":")[0])
        pool_name = self.new_pool_entry.get().strip()
        if not pool_name: messagebox.showerror("Eingabe fehlt",
                                               "Bitte einen Namen für den neuen Pool eingeben."); return
        logger.info(f"Füge neuen Pool '{pool_name}' zu Modul ID {module_id} hinzu.")
        self.db_manager.add_pool(pool_name, module_id);
        self.new_pool_entry.delete(0, tk.END);
        self.on_module_select()

    def on_task_double_click(self, event=None):
        selection = self.task_listbox.curselection();
        if not selection: return
        task_id = int(self.task_listbox.get(selection[0]).split(":")[0]);
        logger.info(f"Bearbeiten-Fenster für Aufgabe ID {task_id} wird geöffnet.")
        task_data = next((task for task in self.tasks_data if task[0] == task_id), None)
        if not task_data: return
        task_content = task_data[1];
        edit_window = Toplevel(self);
        edit_window.title(f"Aufgabe #{task_id} bearbeiten");
        edit_window.geometry("600x400")
        edit_text = scrolledtext.ScrolledText(edit_window, wrap=tk.WORD, height=15);
        edit_text.pack(expand=True, fill="both", padx=10, pady=10);
        edit_text.insert("1.0", task_content)
        button_frame = ttk.Frame(edit_window);
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        save_button = ttk.Button(button_frame, text="Speichern",
                                 command=lambda: self.save_edited_task(task_id, edit_text, edit_window));
        save_button.pack(side="right")
        cancel_button = ttk.Button(button_frame, text="Abbrechen", command=edit_window.destroy);
        cancel_button.pack(side="right", padx=(0, 5))

    def save_edited_task(self, task_id, text_widget, window_to_close):
        new_content = text_widget.get("1.0", tk.END).strip()
        if new_content:
            logger.info(f"Speichere Änderungen für Aufgabe ID {task_id}."); self.db_manager.update_task(task_id,
                                                                                                        new_content); window_to_close.destroy(); self.refresh_task_list()
        else:
            messagebox.showwarning("Leere Aufgabe", "Der Aufgabentext darf nicht leer sein.")

    def update_module_listbox(self):
        logger.debug("Modul-Liste wird aktualisiert.");
        self.modules_data = self.db_manager.get_modules();
        self.module_listbox.delete(0, tk.END)
        for mod_id, name in self.modules_data: self.module_listbox.insert(tk.END, f"{mod_id}: {name}")
        self.pool_listbox.delete(0, tk.END);
        self.task_listbox.delete(0, tk.END)

    def add_new_module(self):
        name = self.new_module_entry.get().strip()
        if not name: return
        logger.info(f"Versuche, neues Modul zu erstellen: '{name}'")
        if self.db_manager.add_module(name):
            self.new_module_entry.delete(0, tk.END); self.controller.on_modules_changed()
        else:
            messagebox.showwarning("Fehler", "Modul existiert bereits.")