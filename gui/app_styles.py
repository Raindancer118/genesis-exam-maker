# gui/app_styles.py
from tkinter import ttk
import logging

logger = logging.getLogger(__name__)

# --- Farb- und Schrift-Palette (Apple-like) ---
BG_COLOR = "#F5F5F7"         # Leicht abgedunkeltes Weiß
FG_COLOR = "#333333"         # Dunkelgrau statt hartem Schwarz
ACCENT_COLOR = "#007AFF"     # Apple's System-Blau
LIGHT_GRAY = "#EAEAEA"
BORDER_COLOR = "#DCDCDC"

BASE_FONT = ("Helvetica", 10)
BOLD_FONT = ("Helvetica", 10, "bold")


def setup_styles(root):
    """Konfiguriert das globale ttk-Styling für ein modernes, helles Design."""
    style = ttk.Style(root)

    try:
        style.theme_use('clam')
        logger.debug("Clam-Theme wird für modernes Styling verwendet.")
    except Exception:
        logger.warning("Clam-Theme nicht verfügbar, Design könnte abweichen.")

    # --- Globale Konfigurationen ---
    style.configure('.',
                    background=BG_COLOR,
                    foreground=FG_COLOR,
                    font=BASE_FONT,
                    borderwidth=0,
                    focuscolor=ACCENT_COLOR)

    # --- Widget-spezifische Stile ---
    style.configure('TFrame', background=BG_COLOR)
    style.configure('TLabel', background=BG_COLOR, foreground=FG_COLOR)

    # Buttons im "Filled" Stil
    style.configure('TButton',
                    background=ACCENT_COLOR,
                    foreground='white',
                    font=BOLD_FONT,
                    bordercolor=ACCENT_COLOR,
                    padding=(10, 5))
    style.map('TButton',
              background=[('active', '#005ecb')]) # Dunkler bei Klick

    # Notebook (Tabs)
    style.configure('TNotebook', background=BG_COLOR, borderwidth=0)
    style.configure('TNotebook.Tab',
                    background=BG_COLOR,
                    foreground='#888888', # Inaktive Tabs sind grau
                    font=BASE_FONT,
                    padding=[15, 8],
                    borderwidth=0)
    style.map('TNotebook.Tab',
              background=[('selected', BG_COLOR)],
              foreground=[('selected', ACCENT_COLOR)])

    # Betont den aktiven Tab mit einer blauen Linie darunter
    style.layout("TNotebook.Tab", [
        ("TNotebook.tab", {
            "sticky": "nswe",
            "children": [
                ("TNotebook.padding", {
                    "side": "top",
                    "sticky": "nswe",
                    "children": [
                        ("TNotebook.focus", {
                            "side": "top",
                            "sticky": "nswe",
                            "children": [("TNotebook.label", {"side": "top", "sticky": ""})]
                        })
                    ]
                }),
                # Diese "underline" ist ein dünner Border am unteren Rand
                ("TNotebook.underline", {"side": "bottom", "sticky": "ew"})
            ]
        })
    ])
    style.configure("TNotebook.underline", background=ACCENT_COLOR, borderwidth=2)
    style.map("TNotebook.Tab",
              underlinecolor=[("selected", ACCENT_COLOR), ("!selected", BG_COLOR)])


    # Eingabefelder und Dropdowns
    style.configure('TEntry',
                    fieldbackground=LIGHT_GRAY,
                    foreground=FG_COLOR,
                    insertcolor=FG_COLOR, # Cursor-Farbe
                    bordercolor=BORDER_COLOR)
    style.configure('TCombobox',
                    fieldbackground=LIGHT_GRAY,
                    foreground=FG_COLOR,
                    arrowcolor=FG_COLOR,
                    selectbackground=LIGHT_GRAY,
                    bordercolor=BORDER_COLOR)
    root.option_add('*TCombobox*Listbox*Background', '#FFFFFF')
    root.option_add('*TCombobox*Listbox*Foreground', FG_COLOR)
    root.option_add('*TCombobox*Listbox*selectBackground', ACCENT_COLOR)
    root.option_add('*TCombobox*Listbox*selectForeground', 'white')

    # Rahmen um Gruppen
    style.configure('TLabelframe',
                    background=BG_COLOR,
                    bordercolor=BORDER_COLOR,
                    padding=10)
    style.configure('TLabelframe.Label',
                    background=BG_COLOR,
                    foreground=FG_COLOR,
                    font=BOLD_FONT)

    # Fortschrittsbalken
    style.configure("blue.Horizontal.TProgressbar",
                    background=ACCENT_COLOR,
                    troughcolor=LIGHT_GRAY,
                    bordercolor=LIGHT_GRAY)