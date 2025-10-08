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
\usepackage{{amsmath, graphicx}}
\usepackage{{unicode-math}}
\setmathfont{{Latin Modern Math}}
% --- HIER IST DIE KORREKTUR für mehr Rand oben und links/rechts auf allen Seiten ---
\usepackage[left=2.5cm, right=2.5cm, top=3.5cm, bottom=2.5cm]{{geometry}} % top=3.5cm für mehr Platz zur Kopfzeile
% --- ENDE DER KORREKTUR ---
\usepackage{{parskip}}
\usepackage{{fancyhdr}}

% --- Kopf- und Fußzeile ---
\pagestyle{{fancy}}
\fancyhf{{}}
% --- HIER IST DIE KORREKTUR: Logo nur auf Titelseite, keine Angabe hier mehr ---
\fancyhead[L]{{NORDAKADEMIE \\ Hochschule der Wirtschaft}} 
% --- ENDE DER KORREKTUR ---
\fancyhead[R]{{Seite \thepage}}
\fancyfoot[C]{{\small made with genesis exam maker}}
\renewcommand{{\headrulewidth}}{{0.4pt}}
\renewcommand{{\footrulewidth}}{{0.4pt}}

\begin{{document}}

% --- Vereinfachtes Deckblatt ---
\begin{{titlepage}}
    \centering
    \vspace*{{1cm}}

    % --- HIER IST DIE KORREKTUR für größeres Logo ---
    \includegraphics[height=5cm]{{assets/genesis-exam-maker.png}} \\ % Logo 2-3x größer
    % --- ENDE DER KORREKTUR ---

    \vspace*{{1cm}} % Abstand zum Text
    \large
    NORDAKADEMIE \\ Hochschule der Wirtschaft

    \vspace*{{3cm}}

    \huge
    \textbf{{{module_name}}}

    \vfill

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


def generate_tex_file(module_name: str, tasks: list[str], output_filename: str):
    logger.info("Konvertiere Markdown und erstelle .tex-Datei...")
    latex_tasks = []
    for i, task_md in enumerate(tasks, 1):
        try:
            latex_content = pypandoc.convert_text(task_md, 'latex', format='md')
            formatted_task = f"\\clearpage\n\\section*{{Aufgabe {i}}}\n{latex_content}\n\\vfill"
            latex_tasks.append(formatted_task)
        except OSError as e:
            msg = f"Pandoc-Fehler: {e}.";
            logger.error(msg);
            return None, msg
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
        if result.returncode == 0:
            result = subprocess.run(command, capture_output=True, text=True)
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
        msg = "Fehler: 'lualatex' nicht gefunden.";
        logger.error(msg);
        return False, msg
    except Exception as e:
        msg = f"Unerwarteter Fehler: {e}";
        logger.error(msg);
        logger.debug(f"LaTeX-Ausgabe:\n{log_content}");
        return False, msg
    finally:
        logger.debug("Räume temporäre Dateien auf...");
        for ext in ['.aux', '.log', '.tex']:
            if os.path.exists(output_filename + ext): os.remove(output_filename + ext)

            # --- convenience wrapper for exam_builder / external callers ---
            from pathlib import Path
            import shutil

            def generate_exam_pdf(module_name, tasks, output_filename: str | None = None):
                """
                High-level helper:
                - prepares output folder (data/generated_exams)
                - makes sure assets/genesis-exam-maker.png is available under <outdir>/assets/
                - calls generate_tex_file(...) and compile_pdf_from_tex(...)
                - returns absolute path to generated PDF or raises RuntimeError on failure
                """
                logger.info("generate_exam_pdf: starting generation...")

                # prepare output directory
                project_root = Path(__file__).resolve().parent.parent
                outdir = project_root / "data" / "generated_exams"
                outdir.mkdir(parents=True, exist_ok=True)

                # ensure logo asset is available to the .tex (template uses assets/...)
                src_asset = project_root / "assets" / "genesis-exam-maker.png"
                if src_asset.exists():
                    try:
                        dst_assets_dir = outdir / "assets"
                        dst_assets_dir.mkdir(exist_ok=True)
                        shutil.copy2(src_asset, dst_assets_dir / src_asset.name)
                    except Exception as e:
                        logger.warning("Konnte Logo nicht kopieren: %s", e)
                else:
                    logger.warning("Logo-Quelle nicht gefunden: %s", src_asset)

                # decide base name (no extension)
                base = (output_filename or module_name or "exam").strip()
                # sanitize some characters for filenames
                base = base.replace(" ", "_")
                if base.lower().endswith(".pdf"):
                    base = base[:-4]

                base_path = str(outdir / base)  # generate_tex_file will append .tex

                # generate .tex
                tex_path, err = generate_tex_file(module_name, tasks, base_path)
                if err:
                    logger.error("generate_tex_file error: %s", err)
                    raise RuntimeError(f"Tex-Generierung fehlgeschlagen: {err}")

                # compile to PDF
                ok, msg = compile_pdf_from_tex(tex_path)
                if not ok:
                    logger.error("LaTeX compile error: %s", msg)
                    raise RuntimeError(f"LaTeX-Kompilierung fehlgeschlagen: {msg}")

                pdf_path = Path(tex_path.replace(".tex", ".pdf")).resolve()
                if not pdf_path.exists():
                    # try expected fallback
                    candidate = outdir / (base + ".pdf")
                    if candidate.exists():
                        pdf_path = candidate.resolve()
                    else:
                        raise RuntimeError(f"PDF nicht gefunden nach Kompilierung (erwartet: {pdf_path})")

                logger.info("generate_exam_pdf: PDF erstellt: %s", str(pdf_path))
                return str(pdf_path)
