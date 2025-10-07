# gui/app_styles.py
from tkinter import ttk

# --- Farbpalette ---
BG_COLOR = "#2E2E2E"
FG_COLOR = "#F0F0F0"
ACCENT_COLOR = "#0078D7"
LIGHT_BG_COLOR = "#3C3C3C"
BORDER_COLOR = "#555555"


def setup_styles(root):
    """Konfiguriert das globale ttk-Styling für die Anwendung."""
    style = ttk.Style(root)

    # Wir verwenden das 'clam'-Theme als Basis, da es am flexibelsten ist
    try:
        style.theme_use('clam')
    except Exception:
        pass  # Fallback auf das Standard-Theme

    # --- Globale Konfigurationen ---
    style.configure('.',
                    background=BG_COLOR,
                    foreground=FG_COLOR,
                    fieldbackground=LIGHT_BG_COLOR,
                    borderwidth=1,
                    focuscolor=ACCENT_COLOR)  # Farbe beim Fokussieren

    # --- Widget-spezifische Stile ---
    style.configure('TFrame', background=BG_COLOR)
    style.configure('TLabel', background=BG_COLOR, foreground=FG_COLOR)
    style.configure('TButton', background=ACCENT_COLOR, foreground='white', bordercolor=ACCENT_COLOR)
    style.map('TButton',
              background=[('active', '#005a9e')])  # Etwas dunkler beim Draufklicken

    style.configure('TNotebook', background=BG_COLOR, borderwidth=0)
    style.configure('TNotebook.Tab',
                    background=LIGHT_BG_COLOR,
                    foreground=FG_COLOR,
                    padding=[10, 5],
                    borderwidth=0)
    style.map('TNotebook.Tab',
              background=[('selected', ACCENT_COLOR), ('active', BG_COLOR)],
              foreground=[('selected', 'white')])

    style.configure('TCombobox',
                    selectbackground=LIGHT_BG_COLOR,
                    fieldbackground=LIGHT_BG_COLOR,
                    background=ACCENT_COLOR)
    # Dropdown-Pfeil anpassen
    root.option_add('*TCombobox*Listbox*Background', LIGHT_BG_COLOR)
    root.option_add('*TCombobox*Listbox*Foreground', FG_COLOR)
    root.option_add('*TCombobox*Listbox*selectBackground', ACCENT_COLOR)
    root.option_add('*TCombobox*Listbox*selectForeground', 'white')

    style.configure('TLabelframe',
                    background=BG_COLOR,
                    foreground=FG_COLOR,
                    bordercolor=BORDER_COLOR,
                    padding=10)
    style.configure('TLabelframe.Label',
                    background=BG_COLOR,
                    foreground=FG_COLOR)

    # --- Spezieller Stil für den Fortschrittsbalken (aus splash_screen.py übernommen) ---
    style.configure("blue.Horizontal.TProgressbar",
                    background=ACCENT_COLOR,
                    troughcolor=LIGHT_BG_COLOR,
                    bordercolor=BORDER_COLOR,
                    lightcolor=ACCENT_COLOR,
                    darkcolor=ACCENT_COLOR)