# gui/splash_screen.py
import tkinter as tk
from tkinter import ttk


class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        self.geometry("400x100")

        # Fenster zentrieren
        parent.update_idletasks()
        width = 400
        height = 100
        x = (parent.winfo_screenwidth() // 2) - (width // 2)
        y = (parent.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        ttk.Label(self, text="Genesis Exam Maker wird gestartet...", font=("Helvetica", 14)).pack(pady=5)
        self.progress_label = ttk.Label(self, text="Initialisiere...")
        self.progress_label.pack(padx=10, anchor="w")
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=380, mode="determinate")
        self.progress_bar.pack(padx=10, pady=5)

        self.lift()  # Sorge dafür, dass es im Vordergrund ist

    def update_progress(self, value, text):
        self.progress_bar['value'] = value
        self.progress_label['text'] = text
        self.update_idletasks()

    def close(self):
        self.destroy()