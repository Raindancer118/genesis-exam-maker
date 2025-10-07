# gui/splash_screen.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import logging

logger = logging.getLogger(__name__)


class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        self.config(bg='white', borderwidth=1, relief='solid')

        # --- Stil für den Fortschrittsbalken definieren ---
        style = ttk.Style(self)
        # Wir stellen sicher, dass wir ein Theme verwenden, das Rundungen unterstützt
        try:
            style.theme_use('clam')
        except tk.TclError:
            logger.warning(
                "Das 'clam'-Theme ist nicht verfügbar. Der Fortschrittsbalken ist möglicherweise nicht abgerundet.")

        # Wir definieren einen neuen Stil und setzen nur die Farben.
        # Die abgerundete Form kommt vom 'clam'-Theme.
        style.configure("blue.Horizontal.TProgressbar",
                        background='#0078D7',  # Ein sattes Blau
                        troughcolor='#FFFFFF',  # Der "Hintergrund" des Balkens
                        bordercolor='#C0C0C0',  # Ein leichter Rand für den Trog
                        lightcolor='#0078D7',
                        darkcolor='#0078D7')

        # --- Logo laden und platzieren ---
        try:
            img = Image.open("assets/genesis-exam-maker.png")
            width, height = img.size
            new_width = 300
            new_height = int(new_width * (height / width))
            img = img.resize((new_width, new_height))

            self.logo_image = ImageTk.PhotoImage(img)
            logo_label = ttk.Label(self, image=self.logo_image, background='white')
            logo_label.pack(pady=(20, 10))
        except Exception as e:
            logger.warning(f"Konnte Splash-Screen-Logo nicht laden: {e}")
            ttk.Label(self, text="Genesis Exam Maker", font=("Helvetica", 16, "bold"), background='white').pack(
                pady=(20, 10))

        # --- Fortschrittsanzeigen mit neuem Stil ---
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=380, mode="determinate",
                                            style="blue.Horizontal.TProgressbar")  # Den neuen Stil anwenden
        # ipady macht den Balken dicker und fördert die Rundung
        self.progress_bar.pack(padx=20, pady=10, ipady=0)

        self.progress_label = ttk.Label(self, text="Initialisiere...", background='white', anchor='w')
        self.progress_label.pack(fill='x', padx=20, pady=(0, 20))

        # --- Fenstergröße und Position anpassen (korrigiert) ---
        win_width = 420
        win_height = 400  # Höhe leicht erhöht für bessere Abstände
        self.geometry(f"{win_width}x{win_height}")

        self.update_idletasks()

        # Fenster jetzt präzise zentrieren
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (win_width // 2)
        y = (screen_height // 8)
        self.geometry(f'+{x}+{y}')

        self.lift()

    def update_progress(self, value, text):
        self.progress_bar['value'] = value
        self.progress_label['text'] = text
        self.update_idletasks()

    def close(self):
        self.destroy()