# core/latex_generator.py
import pypandoc
import subprocess
import os
import logging
from datetime import date

logger = logging.getLogger(__name__)

LATEX_TEMPLATE = r"""
\documentclass[12pt, a4paper]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage{{lmodern}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{graphicx}}
\usepackage[german]{{babel}}
\usepackage[left=2.5cm, right=2.5cm, top=2.5cm, bottom=3cm]{{geometry}}
\usepackage{{parskip}}

\begin{{document}}
\Large\textbf{{Klausur: {module_name}}}\normalsize
\vspace{{0.5cm}}
\begin{{tabular}}{{ll}}
    \textbf{{Datum:}} & {exam_date} \\
    \textbf{{Name:}} & \rule{{8cm}}{{0.4pt}} \\
\end{{tabular}}
\vspace{{0.5cm}}\hrulefill\vspace{{1cm}}
% HIER WERDEN DIE AUFGABEN EINGEFÜGT
\end{{document}}
"""


def generate_exam_pdf(module_name: str, tasks: list[str], output_filename: str):
    logger.info(f"Beginne PDF-Generierung für Modul '{module_name}'...")
    latex_tasks = []
    for i, task_md in enumerate(tasks, 1):
        try:
            latex_content = pypandoc.convert_text(task_md, 'latex', format='md')
            formatted_task = f"\\section*{{Aufgabe {i}}}\n{latex_content}\n\\vfill"
            latex_tasks.append(formatted_task)
        except OSError as e:
            msg = f"Pandoc-Fehler: {e}. Ist Pandoc korrekt installiert?"
            logger.error(msg)
            return False, msg

    full_latex_doc = LATEX_TEMPLATE.format(
        module_name=module_name,
        exam_date=date.today().strftime('%d.%m.%Y'),
    ).replace("% HIER WERDEN DIE AUFGABEN EINGEFÜGT", "\n\n".join(latex_tasks))

    tex_filepath = f"{output_filename}.tex"
    with open(tex_filepath, "w", encoding="utf-8") as f:
        f.write(full_latex_doc)

    try:
        # pdflatex zweimal aufrufen für korrekte Referenzen
        for _ in range(2):
            subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_filepath], check=True, capture_output=True)

        msg = f"PDF '{output_filename}.pdf' erfolgreich erstellt!"
        logger.info(msg)
        return True, msg
    except FileNotFoundError:
        msg = "Fehler: 'pdflatex' nicht gefunden. Ist eine LaTeX-Distribution (wie TeX Live) installiert?"
        logger.error(msg)
        return False, msg
    except subprocess.CalledProcessError as e:
        log_content = e.stdout.decode()
        msg = f"Fehler bei der LaTeX-Kompilierung. Überprüfe die '{output_filename}.log' für Details."
        logger.error(msg)
        logger.debug(f"LaTeX-Fehlerausgabe:\n{log_content}")
        return False, msg
    finally:
        for ext in ['.aux', '.log', '.tex']:
            if os.path.exists(output_filename + ext):
                os.remove(output_filename + ext)