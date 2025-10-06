# core/exam_builder.py
import random
from .database_manager import DatabaseManager
from .latex_generator import generate_exam_pdf


class ExamBuilder:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def build_exam_for_module(self, module_id: int):
        """
        Orchestriert die Erstellung einer Klausur für ein bestimmtes Modul.
        """
        print(f"\nBaue Klausur für Modul-ID {module_id}...")

        # 1. Modulnamen und Konfiguration aus der DB holen
        module_info = self.db.get_module_by_id(module_id)  # Diese Funktion müssen wir noch hinzufügen!
        config_info = self.db.get_exam_config_for_module(module_id)  # Diese auch!

        if not module_info:
            print(f"❌ Fehler: Modul mit ID {module_id} nicht gefunden.")
            return
        if not config_info:
            print(f"❌ Fehler: Keine Klausur-Konfiguration für Modul '{module_info[1]}' gefunden.")
            return

        module_name = module_info[1]
        pool_ids_in_order = config_info[2].split(',')

        print(f"-> Konfiguration gefunden: Reihenfolge der Pools ist {pool_ids_in_order}")

        # 2. Zufällige, einzigartige Aufgaben auswählen
        selected_tasks_content = []
        used_task_ids = set()

        for pool_id_str in pool_ids_in_order:
            pool_id = int(pool_id_str)
            all_tasks_in_pool = self.db.get_tasks_from_pool(pool_id)

            # Filtere bereits verwendete Aufgaben heraus
            available_tasks = [task for task in all_tasks_in_pool if task[0] not in used_task_ids]

            if not available_tasks:
                print(
                    f"⚠️ Warnung: Kein einzigartige Aufgabe mehr in Pool {pool_id} verfügbar! Pool wird übersprungen.")
                continue

            # Wähle eine zufällige Aufgabe
            chosen_task = random.choice(available_tasks)
            selected_tasks_content.append(chosen_task[1])  # Nur den Markdown-Inhalt
            used_task_ids.add(chosen_task[0])  # ID merken, um Duplikate zu vermeiden

            print(f"-> Wähle Aufgabe {chosen_task[0]} aus Pool {pool_id}.")

        # 3. PDF-Generierung anstoßen
        if not selected_tasks_content:
            print("❌ Fehler: Keine Aufgaben konnten ausgewählt werden. Klausur wird nicht erstellt.")
            return

        output_filename = f"Klausur_{module_name.replace(' ', '_')}"
        generate_exam_pdf(module_name, selected_tasks_content, output_filename)