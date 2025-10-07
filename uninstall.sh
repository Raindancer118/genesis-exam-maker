#!/bin/bash

# --- Konfiguration (muss mit install.sh übereinstimmen) ---
APP_NAME="Genesis Exam Maker"
APP_ID="com.genesisexam.maker"
INSTALL_DIR_NAME="GenesisExamMaker"

# --- Pfade ---
INSTALL_PATH="$HOME/.local/lib/$INSTALL_DIR_NAME"
BIN_PATH="$HOME/.local/bin/genesis-exam-maker"
DESKTOP_ENTRY_PATH="$HOME/.local/share/applications/$APP_ID.desktop"
ICON_PATH_DEST="$HOME/.local/share/icons/hicolor/256x256/apps/$APP_ID.png"

echo "Deinstalliere '$APP_NAME'..."

# Alle bei der Installation erstellten Dateien und Ordner löschen
rm -rf "$INSTALL_PATH"
rm -f "$BIN_PATH"
rm -f "$DESKTOP_ENTRY_PATH"
rm -f "$ICON_PATH_DEST"

# Desktop-Datenbank aktualisieren
echo "  -> Aktualisiere Anwendungs-Datenbank..."
update-desktop-database -q "$HOME/.local/share/applications"

echo "Deinstallation abgeschlossen."