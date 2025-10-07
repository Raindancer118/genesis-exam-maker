# core/import_export_manager.py
import pickle
import base64
import json
import logging
from tkinter import messagebox
import os

logger = logging.getLogger(__name__)


def export_data(db_manager, file_path, module_id, pool_id=None):
    """Exportiert ein ganzes Modul oder einen einzelnen Pool in eine Datei."""
    try:
        export_obj = {
            "module_name": db_manager.get_module_by_id(module_id)[1],
            "pools": []
        }

        pools_to_export = []
        if pool_id:  # Nur ein einzelner Pool
            pools_to_export = [p for p in db_manager.get_pools_for_module(module_id) if p[0] == pool_id]
        else:  # Alle Pools des Moduls
            pools_to_export = db_manager.get_pools_for_module(module_id)

        if not pools_to_export:
            raise ValueError("Keine Pools zum Exportieren gefunden.")

        for p_id, p_name in pools_to_export:
            tasks = db_manager.get_tasks_from_pool(p_id)
            task_contents = [content for task_id, content in tasks]
            export_obj["pools"].append({"pool_name": p_name, "tasks": task_contents})

        # Daten serialisieren und kodieren
        pickled_data = pickle.dumps(export_obj)
        base64_data = base64.b64encode(pickled_data).decode('utf-8')

        # Finale JSON-Datei erstellen
        final_export = {
            "format": "genesis_exam_export",
            "version": "1.0",
            "data": base64_data
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(final_export, f, indent=2)

        logger.info(f"Daten erfolgreich nach '{file_path}' exportiert.")
        return True, f"Erfolgreich nach {os.path.basename(file_path)} exportiert."

    except Exception as e:
        logger.error(f"Fehler beim Export: {e}")
        return False, f"Fehler beim Export: {e}"


def import_data(db_manager, file_path, on_conflict):
    """Importiert Daten aus einer Datei und behandelt Duplikate."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            import_json = json.load(f)

        if import_json.get("format") != "genesis_exam_export":
            raise ValueError("Ungültiges Dateiformat.")

        # Daten dekodieren und deserialisieren
        base64_data = import_json["data"].encode('utf-8')
        pickled_data = base64.b64decode(base64_data)
        import_obj = pickle.loads(pickled_data)

        # --- Import-Logik ---
        stats = {"modules_created": 0, "pools_created": 0, "tasks_added": 0, "tasks_skipped": 0}

        # Modul prüfen/erstellen
        module_name = import_obj["module_name"]
        existing_modules = db_manager.get_modules()
        module_id = next((mid for mid, mname in existing_modules if mname == module_name), None)
        if not module_id:
            module_id = db_manager.add_module(module_name)
            stats["modules_created"] += 1

        # Pools und Aufgaben durchgehen
        for pool_data in import_obj["pools"]:
            pool_name = pool_data["pool_name"]
            existing_pools = db_manager.get_pools_for_module(module_id)
            pool_id = next((pid for pid, pname in existing_pools if pname == pool_name), None)
            if not pool_id:
                pool_id = db_manager.add_pool(pool_name, module_id)
                stats["pools_created"] += 1

            # Aufgaben prüfen und importieren
            existing_tasks = {content for tid, content in db_manager.get_tasks_from_pool(pool_id)}
            for task_content in pool_data["tasks"]:
                if task_content in existing_tasks:
                    # Konflikt gefunden
                    action = on_conflict(task_content)  # Rufe die GUI-Funktion für die Entscheidung
                    if action == "skip":
                        stats["tasks_skipped"] += 1
                        continue
                    elif action == "cancel":
                        raise InterruptedError("Import vom Benutzer abgebrochen.")

                db_manager.add_task(task_content, pool_id)
                stats["tasks_added"] += 1

        summary = (f"Import abgeschlossen!\n\n"
                   f"Neue Module: {stats['modules_created']}\n"
                   f"Neue Pools: {stats['pools_created']}\n"
                   f"Neue Aufgaben: {stats['tasks_added']}\n"
                   f"Übersprungene Duplikate: {stats['tasks_skipped']}")
        logger.info(summary)
        return True, summary

    except InterruptedError as e:
        logger.warning(e)
        return False, str(e)
    except Exception as e:
        logger.error(f"Fehler beim Import: {e}")
        return False, f"Fehler beim Import: {e}"