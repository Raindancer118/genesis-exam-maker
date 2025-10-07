# gui/generate_exam_tab.py
import tkinter as tk
from tkinter import ttk, Listbox, messagebox, Toplevel
import logging
import threading
import queue
import random
from core.database_manager import DatabaseManager
from core.latex_generator import generate_tex_file, compile_pdf_from_tex

logger = logging.getLogger(__name__)


class GenerateExamTab(ttk.Frame):
    def __init__(self, parent, controller):
        # ... (init bleibt unverändert)
        super().__init__(parent, padding="10")
        self.controller = controller
        self.db_manager = self.controller.db_manager
        self.modules_data = [];
        self.pools_data = []
        self.setup_widgets()

    def setup_widgets(self):
        # ... (UI-Aufbau bleibt unverändert)
        top_frame = ttk.Frame(self);
        top_frame.pack(fill="x", pady=(0, 10))
        main_frame = ttk.Frame(self);
        main_frame.pack(expand=True, fill="both")
        main_frame.grid_columnconfigure(0, weight=1);
        main_frame.grid_columnconfigure(2, weight=1);
        main_frame.grid_rowconfigure(0, weight=1)
        ttk.Label(top_frame, text="Modul für die Klausur auswählen:").pack(anchor="w")
        self.module_var = tk.StringVar();
        self.module_combo = ttk.Combobox(top_frame, textvariable=self.module_var, state="readonly");
        self.module_combo.pack(fill="x")
        self.module_combo.bind("<<ComboboxSelected>>", self.on_module_selected)
        available_pools_frame = ttk.LabelFrame(main_frame, text="Verfügbare Pools", padding=5);
        available_pools_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.available_pools_listbox = Listbox(available_pools_frame);
        self.available_pools_listbox.pack(expand=True, fill="both")
        button_frame = ttk.Frame(main_frame);
        button_frame.grid(row=0, column=1, padx=5)
        add_button = ttk.Button(button_frame, text=">", command=self.add_pool_to_exam);
        add_button.pack(pady=5)
        remove_button = ttk.Button(button_frame, text="X", command=self.remove_pool_from_exam);
        remove_button.pack(pady=5)
        exam_structure_frame = ttk.LabelFrame(main_frame, text="Klausur-Struktur", padding=5);
        exam_structure_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        self.exam_pools_listbox = Listbox(exam_structure_frame);
        self.exam_pools_listbox.pack(expand=True, fill="both")
        action_frame = ttk.Frame(self);
        action_frame.pack(fill="x", pady=(10, 0))
        self.save_config_button = ttk.Button(action_frame, text="Konfiguration speichern",
                                             command=self.save_configuration);
        self.save_config_button.pack(side="left")
        self.generate_button = ttk.Button(action_frame, text="Klausur generieren!",
                                          command=self.start_generation_process);
        self.generate_button.pack(side="right")

    def start_generation_process(self):
        selected_module_name = self.module_var.get()
        if not selected_module_name: messagebox.showerror("Fehler", "Bitte zuerst ein Modul auswählen."); return
        module_id = self.controller.get_id_from_name(self.modules_data, selected_module_name)
        if not module_id: return

        # --- HIER IST DIE KORREKTUR ---
        # Lese die Pool-Reihenfolge direkt aus der Listbox aus
        pool_items = self.exam_pools_listbox.get(0, tk.END)
        if not pool_items: messagebox.showerror("Fehler", "Die Klausur-Struktur ist leer."); return

        pool_ids_in_order = [item.split(":")[0] for item in pool_items]
        # --- ENDE DER KORREKTUR ---

        self.progress_window = Toplevel(self);
        self.progress_window.title("Generiere Klausur...");
        self.progress_window.geometry("400x80");
        self.progress_window.resizable(False, False);
        self.progress_window.transient(self.controller);
        self.progress_window.grab_set()
        self.progress_label = ttk.Label(self.progress_window, text="Starte Prozess...");
        self.progress_label.pack(padx=10, pady=5, anchor="w")
        self.progress_bar = ttk.Progressbar(self.progress_window, orient="horizontal", length=380, mode="determinate");
        self.progress_bar.pack(padx=10, pady=5)

        self.progress_queue = queue.Queue()
        # Übergebe die ausgelesene Reihenfolge an den Worker-Thread
        args = (module_id, selected_module_name, pool_ids_in_order, self.progress_queue)
        threading.Thread(target=self._compilation_worker, args=args, daemon=True).start()
        self.after(100, self._process_queue)

    def _process_queue(self):
        # ... (unverändert)
        try:
            progress, text, result_data = self.progress_queue.get_nowait()
            if progress == "DONE": self.progress_window.destroy(); success, message = result_data; (
                messagebox.showinfo if success else messagebox.showerror)("Ergebnis", message); return
            self.progress_bar['value'] = progress;
            self.progress_label['text'] = text
        except queue.Empty:
            pass
        self.after(100, self._process_queue)

    def _compilation_worker(self, module_id, module_name, pool_ids_in_order, q):
        db_manager_thread = None
        try:
            db_manager_thread = DatabaseManager()
            q.put((10, "Stelle Aufgaben zusammen...", None))

            selected_tasks_content = [];
            used_task_ids = set()
            for pool_id_str in pool_ids_in_order:
                pool_id = int(pool_id_str)
                all_tasks = db_manager_thread.get_tasks_from_pool(pool_id)
                available = [t for t in all_tasks if t[0] not in used_task_ids]
                if not available: continue
                chosen = random.choice(available)
                selected_tasks_content.append(chosen[1]);
                used_task_ids.add(chosen[0])

            if not selected_tasks_content: raise ValueError("Es konnten keine Aufgaben ausgewählt werden.")

            q.put((40, "Konvertiere Markdown zu LaTeX...", None))
            output_filename = f"Klausur_{module_name.replace(' ', '_')}"

            # Übergebe die Anzahl der Aufgaben für die Punktetabelle
            tex_filepath, error = generate_tex_file(module_name, selected_tasks_content, output_filename)
            if error: raise RuntimeError(error)

            q.put((70, "Kompiliere PDF mit LuaLaTeX...", None))
            success, message = compile_pdf_from_tex(tex_filepath)

            q.put(("DONE", "Fertig!", (success, message)))
        except Exception as e:
            logger.error(f"Fehler im Worker-Thread: {e}")
            q.put(("DONE", "Fehler!", (False, str(e))))
        finally:
            if db_manager_thread: db_manager_thread.close()

    # --- Restliche Methoden (unverändert) ---
    def update_module_dropdown(self):
        self.modules_data = self.db_manager.get_modules(); self.module_combo['values'] = [n for i, n in
                                                                                          self.modules_data]; self.clear_lists()

    def on_module_selected(self, event=None):
        self.clear_lists();
        name = self.module_var.get();
        if not name: return
        module_id = self.controller.get_id_from_name(self.modules_data, name);
        if not module_id: return
        self.pools_data = self.db_manager.get_pools_for_module(module_id)
        for pid, pname in self.pools_data: self.available_pools_listbox.insert(tk.END, f"{pid}: {pname}")
        config = self.db_manager.get_exam_config_for_module(module_id)
        if config and config[2]:
            pool_dict = {str(p_id): p_name for p_id, p_name in self.pools_data}
            for p_id in config[2].split(','):
                if p_id in pool_dict: self.exam_pools_listbox.insert(tk.END, f"{p_id}: {pool_dict[p_id]}")

    def add_pool_to_exam(self):
        sel = self.available_pools_listbox.curselection(); \
                (sel and self.exam_pools_listbox.insert(tk.END, self.available_pools_listbox.get(sel[0])))

    def remove_pool_from_exam(self):
        sel = self.exam_pools_listbox.curselection(); (sel and self.exam_pools_listbox.delete(sel[0]))

    def save_configuration(self):
        name = self.module_var.get();
        if not name: messagebox.showerror("Fehler", "Bitte zuerst ein Modul auswählen."); return
        module_id = self.controller.get_id_from_name(self.modules_data, name);
        if not module_id: return
        pool_items = self.exam_pools_listbox.get(0, tk.END)
        pool_ids = [item.split(":")[0] for item in pool_items]
        self.db_manager.save_exam_config(module_id, ",".join(pool_ids))
        messagebox.showinfo("Gespeichert", f"Konfiguration für '{name}' wurde gespeichert.")

    def clear_lists(self):
        self.available_pools_listbox.delete(0, tk.END); self.exam_pools_listbox.delete(0, tk.END)