# core/latex_generator.py
import pypandoc
import subprocess
import os
from datetime import date

# Ein robustes LaTeX-Template.
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

\Large
\textbf{{Klausur: {module_name}}}
\normalsize

\vspace{{0.5cm}}
\begin{{tabular}}{{ll}}
    \textbf{{Datum:}} & {exam_date} \\
    \textbf{{Name:}} & \rule{{8cm}}{{0.4pt}} \\
\end{{tabular}}
\vspace{{0.5cm}}
\hrulefill
\vspace{{1cm}}

% HIER WERDEN DIE AUFGABEN EINGEFÜGT

\end{{document}}
"""



def generate_exam_pdf(module_name: str, tasks: list[str], output_filename: str):
    """
    Erstellt aus einer Liste von Markdown-Aufgaben eine fertige Klausur-PDF.
    """
    print(f"📄 Beginne PDF-Generierung für Modul '{module_name}'...")

    # 1. Markdown-Aufgaben in LaTeX-Code umwandeln
    latex_tasks = []
    for i, task_md in enumerate(tasks, 1):
        try:
            # Nutze pypandoc zur Konvertierung
            latex_content = pypandoc.convert_text(task_md, 'latex', format='md')

            # Formatiere die Aufgabe mit Titel und Platz für Antworten
            # \vspace*{5cm} erzwingt den Platz, auch am Seitenende
            formatted_task = f"\\section*{{Aufgabe {i}}}\n{latex_content}\n\\vfill"
            latex_tasks.append(formatted_task)
        except OSError as e:
            print(f"❌ Pandoc-Fehler: {e}. Ist Pandoc installiert?")
            return False

    # 2. Aufgaben in das Haupt-Template einfügen
    full_latex_doc = LATEX_TEMPLATE.format(
        module_name=module_name,
        exam_date=date.today().strftime('%d.%m.%Y'),
    )
    full_latex_doc = full_latex_doc.replace(
        "% HIER WERDEN DIE AUFGABEN EINGEFÜGT",
        "\n\n".join(latex_tasks)
    )

    # 3. .tex-Datei schreiben
    tex_filepath = f"{output_filename}.tex"
    with open(tex_filepath, "w", encoding="utf-8") as f:
        f.write(full_latex_doc)

    # 4. LaTeX zu PDF kompilieren (benötigt pdflatex)
    try:
        # Wir rufen pdflatex zweimal auf, um Referenzen etc. korrekt aufzulösen
        subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_filepath], check=True, capture_output=True)
        subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_filepath], check=True, capture_output=True)
        print(f"✅ PDF '{output_filename}.pdf' erfolgreich erstellt!")
        return True
    except FileNotFoundError:
        print(
            "❌ Fehler: 'pdflatex' nicht gefunden. Ist eine LaTeX-Distribution (MiKTeX, TeX Live) installiert und im PATH?")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler bei der LaTeX-Kompilierung. Überprüfe die '{output_filename}.log' für Details.")
        print(e.stdout.decode())
        return False
    finally:
        # 5. Aufräumen der temporären Dateien
        for ext in ['.aux', '.log', '.tex']:
            if os.path.exists(output_filename + ext):
                os.remove(output_filename + ext)