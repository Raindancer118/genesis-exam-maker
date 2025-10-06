# main.py
from gui.main_window import KlausurApp

if __name__ == '__main__':
    app = KlausurApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing) # Stellt sicher, dass die DB-Verbindung schließt
    app.mainloop()