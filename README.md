# Genesis Exam Maker

Ein in Python geschriebenes Desktop-Programm zur einfachen Verwaltung von Klausuraufgaben und zur automatischen Generierung von Klausur-PDFs mit LaTeX.

## ✨ Features

  * **Grafische Benutzeroberfläche** zur Verwaltung von Modulen, Aufgabenpools und einzelnen Aufgaben.
  * Eingabe der Aufgaben im einfachen **Markdown-Format**.
  * Dynamische **PDF-Generierung** mit einer professionellen LuaLaTeX-Engine.
  * **Anpassbare Klausurstruktur** durch Zusammenstellung von Aufgabenpools.
  * **Import & Export** von Aufgabensammlungen zur einfachen Weitergabe und Sicherung.
  * Modernes, anpassbares User Interface.
  * **System-Check** beim Start zur Überprüfung der Abhängigkeiten.

## 🚀 Installation (Linux)

Um den Genesis Exam Maker zu installieren, müssen zuerst die System-Voraussetzungen erfüllt und danach das Installations-Skript ausgeführt werden.

### 1\. System-Voraussetzungen

Stelle sicher, dass die folgenden Programme auf deinem System installiert sind.

#### a) Python 3 & Pip

(Unter den meisten modernen Linux-Distributionen bereits vorinstalliert)

```bash
# Beispiel für Arch/Manjaro
sudo pacman -S python python-pip
```

#### b) Pandoc

```bash
# Beispiel für Arch/Manjaro
sudo pacman -S pandoc
```

#### c) TeX Live (LaTeX-Distribution)

```bash
# Beispiel für Arch/Manjaro
sudo pacman -S texlive-core texlive-bin texlive-langgerman texlive-fontsextra texlive-latexextra
```

### 2\. Anwendung installieren

1.  Lade das neueste Release-Archiv herunter (z.B. `GenesisExamMaker-Python-v1.0.tar.gz`).
2.  Entpacke das Archiv in einem Ordner deiner Wahl:
    ```bash
    tar -xzvf GenesisExamMaker-Python-v1.0.tar.gz
    ```
3.  Wechsle in das neu erstellte Verzeichnis und führe das Installations-Skript aus:
    ```bash
    cd GenesisExamMaker-Python-v1.0
    bash install.sh
    ```

Das Skript kopiert die Anwendung, installiert die Python-Abhängigkeiten in einem eigenen Virtual Environment und erstellt einen Eintrag im Anwendungsmenü.

### 3\. Anwendung starten

Nach der Installation kannst du **Genesis Exam Maker** einfach über das Startmenü deiner Desktop-Umgebung finden und starten.

-----

## 🚀 Installation (Windows)

Unter Windows erfolgt die Installation manuell, indem die Voraussetzungen installiert und die Anwendung in einer eigenen Umgebung ausgeführt wird.

### 1\. System-Voraussetzungen

Stelle sicher, dass die folgenden Programme auf deinem System installiert sind.

#### a) Python 3

  * Lade den neuesten Python-Installer von der [offiziellen Python-Webseite](https://www.python.org/downloads/windows/) herunter.
  * Führe den Installer aus. **Wichtig:** Setze während der Installation den Haken bei **"Add Python to PATH"**.

#### b) Pandoc

  * Lade den `.msi`-Installer für Windows von der [Pandoc-Webseite](https://pandoc.org/installing.html) herunter.
  * Führe den Installer mit den Standardeinstellungen aus.

#### c) MiKTeX (LaTeX-Distribution)

  * Lade den MiKTeX-Installer von der [offiziellen MiKTeX-Webseite](https://miktex.org/download) herunter.
  * Führe den Installer aus. Wähle die Option "Install MiKTeX for: Only for me" (empfohlen).
  * **Wichtig:** Stelle im Schritt "Settings" sicher, dass die Option **"Install missing packages on-the-fly"** auf **"Yes"** oder **"Ask me first"** gestellt ist. Dadurch kann LaTeX benötigte Pakete automatisch nachinstallieren.

### 2\. Anwendung einrichten

1.  Lade das neueste Release-Archiv herunter (z.B. `GenesisExamMaker-Python-v1.0.zip`).
2.  Entpacke das Archiv in einem permanenten Ordner deiner Wahl (z.B. `C:\Users\DeinName\Anwendungen\GenesisExamMaker`).

### 3\. Anwendung starten

Die Anwendung wird aus der Kommandozeile gestartet.

1.  Öffne eine **Eingabeaufforderung** (CMD) oder **PowerShell**.
2.  Navigiere in das Verzeichnis, in das du die Anwendung entpackt hast:
    ```powershell
    cd C:\Users\DeinName\Anwendungen\GenesisExamMaker
    ```
3.  Erstelle einmalig eine virtuelle Umgebung:
    ```powershell
    python -m venv venv
    ```
4.  Aktiviere die virtuelle Umgebung. **Dieser Schritt muss jedes Mal vor dem Start der App wiederholt werden.**
    ```powershell
    .\venv\Scripts\activate
    ```
5.  Installiere einmalig die notwendigen Python-Pakete:
    ```powershell
    pip install -r requirements.txt
    ```
6.  Starte die Anwendung:
    ```powershell
    python main.py
    ```

### Optional: Desktop-Verknüpfung erstellen

Um das Starten zu vereinfachen, kannst du eine Verknüpfung erstellen, die alle Schritte automatisch ausführt.

1.  Klicke mit der rechten Maustaste auf den Desktop und wähle **Neu -\> Verknüpfung**.
2.  Gib als "Speicherort des Elements" den folgenden Befehl ein (passe den Pfad zu deinem Projekt an):
    ```
    cmd.exe /c "cd C:\Users\DeinName\Anwendungen\GenesisExamMaker && .\venv\Scripts\activate && python main.py"
    ```
3.  Gib der Verknüpfung einen Namen (z.B. "Genesis Exam Maker").
4.  (Optional) Klicke mit rechts auf die neue Verknüpfung -\> **Eigenschaften** -\> **Anderes Symbol...** und wähle das `genesis-exam-maker.png` aus dem `assets`-Ordner deines Projektverzeichnisses aus.