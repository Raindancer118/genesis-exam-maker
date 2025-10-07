#!/bin/bash

# --- Konfiguration ---
APP_NAME="Genesis Exam Maker"
APP_ID="com.genesisexam.maker"
INSTALL_DIR_NAME="GenesisExamMaker"
ICON_NAME="genesis-exam-maker.png"

# --- Pfade ---
INSTALL_PATH="$HOME/.local/lib/$INSTALL_DIR_NAME"
BIN_PATH="$HOME/.local/bin"
DESKTOP_ENTRY_PATH="$HOME/.local/share/applications/$APP_ID.desktop"
ICON_PATH_DEST="$HOME/.local/share/icons/hicolor/256x256/apps/$APP_ID.png"

echo "Installiere '$APP_NAME' als Python-Anwendung..."

# 1. Prüfen, ob Python und pip vorhanden sind
if ! command -v python3 &> /dev/null || ! command -v pip &> /dev/null; then
    echo "FEHLER: python3 und/oder pip wurden nicht gefunden. Bitte installiere Python 3."
    exit 1
fi

# 2. Alte Installationen entfernen
echo "  -> Entferne alte Versionen..."
rm -rf "$INSTALL_PATH"
rm -f "$BIN_PATH/genesis-exam-maker"
rm -f "$DESKTOP_ENTRY_PATH"
rm -f "$ICON_PATH_DEST"

# 3. Verzeichnisse erstellen
echo "  -> Erstelle Verzeichnisse..."
mkdir -p "$INSTALL_PATH"
mkdir -p "$BIN_PATH"
mkdir -p "$(dirname "$DESKTOP_ENTRY_PATH")"
mkdir -p "$(dirname "$ICON_PATH_DEST")"

# 4. Projektdateien kopieren (alles aus dem aktuellen Ordner)
echo "  -> Kopiere Anwendungsdateien..."
cp -r ./* "$INSTALL_PATH/"

# 5. Ein Virtual Environment erstellen und Abhängigkeiten installieren
echo "  -> Erstelle Virtual Environment und installiere Abhängigkeiten..."
python3 -m venv "$INSTALL_PATH/venv"
source "$INSTALL_PATH/venv/bin/activate"
pip install -r "$INSTALL_PATH/requirements.txt"
deactivate

# 6. Ein Start-Skript im bin-Verzeichnis erstellen
echo "  -> Erstelle Startbefehl 'genesis-exam-maker'..."
cat > "$BIN_PATH/genesis-exam-maker" <<EOL
#!/bin/bash
# Wechselt in das Verzeichnis der App, aktiviert das venv und startet sie
cd "$INSTALL_PATH"
source ./venv/bin/activate
python main.py
EOL
chmod +x "$BIN_PATH/genesis-exam-maker"

# 7. Die .desktop-Datei für das Anwendungsmenü erstellen
echo "  -> Erstelle Menüeintrag..."
cp "$INSTALL_PATH/assets/$ICON_NAME" "$ICON_PATH_DEST"
cat > "$DESKTOP_ENTRY_PATH" <<EOL
[Desktop Entry]
Version=1.0
Name=$APP_NAME
Comment=Klausuraufgaben verwalten und generieren
Exec=genesis-exam-maker
Icon=$APP_ID
Terminal=false
Type=Application
Categories=Office;Education;
EOL

# 8. Desktop-Datenbank aktualisieren
echo "  -> Aktualisiere Anwendungs-Datenbank..."
update-desktop-database -q "$HOME/.local/share/applications"

echo ""
echo "Installation abgeschlossen!"
echo "Du kannst '$APP_NAME' jetzt aus deinem Anwendungsmenü starten."