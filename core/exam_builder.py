# core/exam_builder.py
import random
import logging
from .database_manager import DatabaseManager
from .latex_generator import generate_tex_file, compile_pdf_from_tex

logger = logging.getLogger(__name__)


class ExamBuilder:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def build_exam_for_module(self, module_id: int):

        logger.info(f"Baue Klausur für Modul-ID {module_id}...")

        module_info = self.db.get_module_by_id(module_id)
        config_info = self.db.get_exam_config_for_module(module_id)

        if not module_info:
            msg = f"Fehler: Modul mit ID {module_id} nicht gefunden."
            logger.error(msg)
            return False, msg
        if not config_info or not config_info[2]:
            msg = f"Fehler: Keine oder leere Klausur-Konfiguration für Modul '{module_info[1]}' gefunden."
            logger.error(msg)
            return False, msg

        module_name = module_info[1]
        pool_ids_in_order = config_info[2].split(',')
        logger.debug(f"-> Konfiguration gefunden: Reihenfolge der Pools ist {pool_ids_in_order}")

        selected_tasks_content = []
        used_task_ids = set()

        for pool_id_str in pool_ids_in_order:
            pool_id = int(pool_id_str)
            all_tasks_in_pool = self.db.get_tasks_from_pool(pool_id)
            available_tasks = [task for task in all_tasks_in_pool if task[0] not in used_task_ids]

            if not available_tasks:
                msg = f"Warnung: Kein einzigartige Aufgabe mehr in Pool {pool_id} verfügbar! Pool wird übersprungen."
                logger.warning(msg)
                continue

            chosen_task = random.choice(available_tasks)
            selected_tasks_content.append(chosen_task[1])
            used_task_ids.add(chosen_task[0])
            logger.debug(f"-> Wähle Aufgabe {chosen_task[0]} aus Pool {pool_id}.")

        if not selected_tasks_content:
            msg = "Fehler: Es konnten keine Aufgaben ausgewählt werden. Klausur wird nicht erstellt."
            logger.error(msg)
            return False, msg

        output_filename = f"Klausur_{module_name.replace(' ', '_')}"
        success, message = generate_exam_pdf(module_name, selected_tasks_content, output_filename)

        return success, message