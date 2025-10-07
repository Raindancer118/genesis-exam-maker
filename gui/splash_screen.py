# gui/splash_screen.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import logging

logger = logging.getLogger(__name__)


class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)  # Fenster ohne Titelleiste
        self.config(bg='white', borderwidth=1, relief='solid')  # Weißer Hintergrund, dünner schwarzer Rand

        # --- Logo laden und platzieren ---
        try:
            img = Image.open("assets/genesis-exam-maker.png")
            # Bildgröße anpassen, falls nötig (z.B. auf 300 Pixel Breite)
            width, height = img.size
            new_width = 300
            new_height = int(new_width * (height / width))
            img = img.resize((new_width, new_height))

            self.logo_image = ImageTk.PhotoImage(img)
            logo_label = ttk.Label(self, image=self.logo_image, background='white')
            logo_label.pack(pady=(20, 10))
        except Exception as e:
            logger.warning(f"Konnte Splash-Screen-Logo nicht laden: {e}")
            # Fallback-Text, falls das Logo nicht gefunden wird
            ttk.Label(self, text="Genesis Exam Maker", font=("Helvetica", 16, "bold"), background='white').pack(
                pady=(20, 10))

        # --- Fortschrittsanzeigen ---
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=380, mode="determinate")
        self.progress_bar.pack(padx=20, pady=5)

        self.progress_label = ttk.Label(self, text="Initialisiere...", background='white')
        self.progress_label.pack(padx=20, pady=(0, 10), anchor="w")

        # --- Fenstergröße und Position anpassen ---
        win_width = 420
        win_height = 220  # Etwas höher für das Logo
        self.geometry(f"{win_width}x{win_height}")

        parent.update_idletasks()
        x = (parent.winfo_screenwidth() // 2) - (win_width // 2)
        y = (parent.winfo_screenheight() // 2) - (win_height // 2)
        self.geometry(f'+{x}+{y}')

        self.lift()

    def update_progress(self, value, text):
        self.progress_bar['value'] = value
        self.progress_label['text'] = text
        self.update_idletasks()

    def close(self):
        self.destroy()