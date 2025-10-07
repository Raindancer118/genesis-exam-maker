# core/latex_generator.py
import pypandoc
import subprocess
import os
import logging
from datetime import date

logger = logging.getLogger(__name__)

# Neues, professionelles Template im Stil der Probeklausur
LATEX_TEMPLATE = r"""
\documentclass[12pt, a4paper,ngerman]{{article}}
\usepackage{{babel}}
\usepackage{{fontspec}}
\usepackage{{unicode-math}}
\setmainfont{{TeX Gyre Termes}} % Eine hochwertige Alternative zu Times New Roman
\setsansfont{{TeX Gyre Heros}}   % Eine Alternative zu Helvetica
\setmonofont{{TeX Gyre Cursor}}  % Eine gute, nichtproportionale Schriftart
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{graphicx}}
\usepackage[left=2.5cm, right=2.5cm, top=3.5cm, bottom=3cm]{{geometry}} % Mehr Platz für Kopfzeile
\usepackage{{parskip}}

% --- Pakete für professionelles Layout ---
\usepackage{{xcolor}}      % Für Farben
\usepackage{{listings}}    % Für Code-Formatierung
\usepackage{{fancyhdr}}    % Für Kopf- und Fußzeilen

% --- Konfiguration der Kopfzeile ---
\pagestyle{{fancy}}
\fancyhf{{}} % Alte Kopf- und Fußzeilen leeren
\fancyhead[L]{{NORDAKADEMIE \\ Hochschule der Wirtschaft}}
\fancyhead[R]{{Seite \thepage}}
\renewcommand{{\headrulewidth}}{{0.4pt}}
\renewcommand{{\footrulewidth}}{{0pt}}

% --- Konfiguration für Code-Blöcke (listings) ---
\definecolor{{codegreen}}{{rgb}}{{0,0.6,0}}
\definecolor{{codegray}}{{rgb}}{{0.5,0.5,0.5}}
\definecolor{{codepurple}}{{rgb}}{{0.58,0,0.82}}
\definecolor{{backcolour}}{{rgb}}{{0.95,0.95,0.95}}

\lstdefinestyle{{customjava}}{{
    backgroundcolor=\color{{backcolour}},   
    commentstyle=\color{{codegreen}},
    keywordstyle=\color{{blue}},
    numberstyle=\tiny\color{{codegray}},
    stringstyle=\color{{codepurple}},
    basicstyle=\ttfamily\footnotesize,
    breakatwhitespace=false,         
    breaklines=true,                 
    captionpos=b,                    
    keepspaces=true,                 
    numbers=left,                    
    numbersep=5pt,                  
    showspaces=false,                
    showstringspaces=false,
    showtabs=false,                  
    tabsize=2,
    language=Java
}}

\begin{{document}}

% --- Titelfeld (optional, kann angepasst werden) ---
\begin{{center}}
    \Large\textbf{{Klausur: {module_name}}} \\
    \large\textbf{{Datum: {exam_date}}}
\end{{center}}
\vspace{{0.5cm}}
\noindent Name: \rule[0.1em]{{0.4\linewidth}}{{0.4pt}} \hfill Matrikelnummer: \rule[0.1em]{{0.3\linewidth}}{{0.4pt}}
\hrulefill
\vspace{{1cm}}

% HIER WERDEN DIE AUFGABEN EINGEFÜGT

\end{{document}}
"""

def generate_tex_file(module_name: str, tasks: list[str], output_filename: str):
    logger.info("Konvertiere Markdown und erstelle .tex-Datei...")
    latex_tasks = []
    for i, task_md in enumerate(tasks, 1):
        try:
            # HIER IST DIE WICHTIGE ANPASSUNG für Code-Blöcke:
            latex_content = pypandoc.convert_text(
                task_md,
                'latex',
                format='md',
                extra_args=['--listings'] # Sorgt dafür, dass Code-Blöcke ``` ... ``` das listings-Paket verwenden
            )
            # Wir definieren das Standard-Listing-Format für alle Code-Blöcke
            formatted_task = f"\\lstset{{style=customjava}}\n\\section*{{Aufgabe {i}}}\n{latex_content}\n\\vfill"
            latex_tasks.append(formatted_task)
        except OSError as e:
            msg = f"Pandoc-Fehler: {e}. Ist Pandoc korrekt installiert?"
            logger.error(msg); return None, msg

    full_latex_doc = LATEX_TEMPLATE.format(
        module_name=module_name,
        exam_date=date.today().strftime('%d.%m.%Y'),
    ).replace("% HIER WERDEN DIE AUFGABEN EINGEFÜGT", "\n\n".join(latex_tasks))
    tex_filepath = f"{output_filename}.tex"
    with open(tex_filepath, "w", encoding="utf-8") as f:
        f.write(full_latex_doc)
    return tex_filepath, None

def compile_pdf_from_tex(tex_filepath: str):
    # Diese Funktion bleibt unverändert und nutzt weiterhin LuaLaTeX
    output_filename = tex_filepath.replace(".tex", "")
    log_content = ""
    try:
        command = ["lualatex", "-interaction=nonstopmode", tex_filepath]
        logger.info("Führe lualatex aus...")
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
             result = subprocess.run(command, capture_output=True, text=True)
        log_content = result.stdout
        if os.path.exists(f"{output_filename}.pdf"):
            msg = f"PDF '{output_filename}.pdf' erfolgreich erstellt!"
            logger.info(msg)
            return True, msg
        else:
            msg = "Fehler bei der LaTeX-Kompilierung. Es wurde keine PDF erstellt."
            logger.error(msg); logger.debug(f"LaTeX-Ausgabe:\n{log_content}"); return False, msg
    except FileNotFoundError:
        msg = "Fehler: 'lualatex' nicht gefunden."
        logger.error(msg); return False, msg
    except Exception as e:
        msg = f"Ein unerwarteter Fehler ist aufgetreten: {e}"
        logger.error(msg); logger.debug(f"LaTeX-Ausgabe:\n{log_content}"); return False, msg
    finally:
        logger.debug("Räume temporäre Dateien auf...")
        for ext in ['.aux', '.log', '.tex']:
             if os.path.exists(output_filename + ext):
                os.remove(output_filename + ext)