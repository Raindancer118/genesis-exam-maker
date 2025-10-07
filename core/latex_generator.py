# core/latex_generator.py
import pypandoc
import subprocess
import os
import logging
from datetime import date

logger = logging.getLogger(__name__)

LATEX_TEMPLATE = r"""
\documentclass[12pt, a4paper,ngerman]{{article}}
\usepackage{{babel}}
\usepackage{{fontspec}}
\setmainfont{{TeX Gyre Termes}}
\usepackage{{amsmath, amssymb, graphicx}}
\usepackage[left=2.5cm, right=2.5cm, top=2.5cm, bottom=2.5cm]{{geometry}}
\usepackage{{parskip}}
\usepackage{{fancyhdr}}

% --- Kopf- und Fußzeile ---
\pagestyle{{fancy}}
\fancyhf{{}}
% HIER DAS ICON IN DER KOPFZEILE
\fancyhead[L]{{\includegraphics[height=1cm]{{assets/genesis-exam-maker.png}} \hspace{{1cm}} NORDAKADEMIE \\ Hochschule der Wirtschaft}}
\fancyhead[R]{{Seite \thepage}}
\fancyfoot[C]{{\small made with genesis exam maker}}
\renewcommand{{\headrulewidth}}{{0.4pt}}
\renewcommand{{\footrulewidth}}{{0.4pt}}

\begin{{document}}

% --- Vereinfachtes Deckblatt ---
\begin{{titlepage}}
    \centering
    \vspace*{{1cm}}

    \includegraphics[height=2cm]{{assets/genesis-exam-maker.png}} \\
    \vspace*{{1cm}}
    \large
    NORDAKADEMIE \\ Hochschule der Wirtschaft

    \vspace*{{3cm}}

    \huge
    \textbf{{{module_name}}}

    \vfill % Flexibler Abstand nach unten

    \begin{{minipage}}{{0.8\textwidth}}
        \large
        \begin{{flushleft}}
            Name des Prüflings: \rule[0.1em]{{0.6\linewidth}}{{0.4pt}} \\
            \vspace*{{0.5cm}}
            Matrikelnummer: \rule[0.1em]{{0.65\linewidth}}{{0.4pt}} \\
            \vspace*{{0.5cm}}
            Zenturie: \rule[0.1em]{{0.75\linewidth}}{{0.4pt}}
        \end{{flushleft}}
    \end{{minipage}}

\end{{titlepage}}

% HIER WERDEN DIE AUFGABEN EINGEFÜGT
\end{{document}}
"""


# NEUE FUNKTION für den Startup-Check
def run_test_compilation():
    """Führt eine stille Test-Kompilierung mit einem minimalen Dokument durch."""
    test_content = r"\documentclass{{article}}\begin{{document}}Test\end{{document}}"
    test_filename = "startup_test"

    with open(f"{test_filename}.tex", "w") as f:
        f.write(test_content)

    try:
        command = ["lualatex", "-interaction=batchmode", test_filename]
        # Führe den Befehl aus, ohne auf den Output zu warten
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(f"{test_filename}.pdf"):
            logger.info("Test-Kompilierung erfolgreich.")
            return True, "OK"
        else:
            return False, "Kompilierung lief durch, aber es wurde keine PDF erstellt."
    except Exception as e:
        logger.error(f"Fehler bei Test-Kompilierung: {e}")
        return False, str(e)
    finally:
        for ext in ['.aux', '.log', '.tex', '.pdf']:
            if os.path.exists(test_filename + ext):
                os.remove(test_filename + ext)


def generate_tex_file(module_name: str, tasks: list[str], output_filename: str):
    logger.info("Konvertiere Markdown und erstelle .tex-Datei...")
    latex_tasks = []
    for i, task_md in enumerate(tasks, 1):
        try:
            # pypandoc wird pandoc jetzt automatisch im System finden
            latex_content = pypandoc.convert_text(task_md, 'latex', format='md')
            formatted_task = f"\\clearpage\n\\section*{{Aufgabe {i}}}\n{latex_content}\n\\vfill"
            latex_tasks.append(formatted_task)
        except OSError as e:
            msg = f"Pandoc-Fehler: {e}."
            logger.error(msg);
            return None, msg
    # ... (der Rest der Funktion ist korrekt)
    full_latex_doc = LATEX_TEMPLATE.format(
        module_name=module_name,
    ).replace("% HIER WERDEN DIE AUFGABEN EINGEFÜGT", "\n".join(latex_tasks))
    tex_filepath = f"{output_filename}.tex"
    with open(tex_filepath, "w", encoding="utf-8") as f:
        f.write(full_latex_doc)
    return tex_filepath, None


def compile_pdf_from_tex(tex_filepath: str):
    output_filename = tex_filepath.replace(".tex", "")
    log_content = ""
    try:
        command = ["lualatex", "-interaction=nonstopmode", tex_filepath]
        logger.info("Führe lualatex aus...");
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0: result = subprocess.run(command, capture_output=True, text=True)
        log_content = result.stdout
        if os.path.exists(f"{output_filename}.pdf"):
            msg = f"PDF '{output_filename}.pdf' erfolgreich erstellt!";
            logger.info(msg);
            return True, msg
        else:
            msg = "Fehler: Keine PDF erstellt.";
            logger.error(msg);
            logger.debug(f"LaTeX-Ausgabe:\n{log_content}");
            return False, msg
    except FileNotFoundError:
        msg = "Fehler: 'lualatex' nicht gefunden."; logger.error(msg); return False, msg
    except Exception as e:
        msg = f"Unerwarteter Fehler: {e}"; logger.error(msg); logger.debug(
            f"LaTeX-Ausgabe:\n{log_content}"); return False, msg
    finally:
        logger.debug("Räume temporäre Dateien auf...");
        for ext in ['.aux', '.log', '.tex']:
            if os.path.exists(output_filename + ext): os.remove(output_filename + ext)