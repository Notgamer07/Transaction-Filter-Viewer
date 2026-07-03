# Account Statement Analyzer

A cross-platform desktop application built with Python and Tkinter that allows users to seamlessly import, clean, filter, and color-code bank account statements. It features dynamic drag-and-drop file imports, a smart narration search, and automatic financial calculations formatted using the Indian Numbering System.

## Features

* **Dual File Intake:** Import CSV files via native file browser or by dropping them anywhere inside the drag-and-drop landing zone.
* **Smart Raw Log Parser:** Automatically strips away header metadata rows, cleans empty spacer columns, and clips annoying mid-string timestamps (`HH:MM:SS`) out of the `NARRATION` logs automatically.
* **Real-time Narration Filter:** Type strings inside the search filter to query rows matching descriptions dynamically on the fly.
* **Transaction Mode Dropdown:** Isolate records cleanly via *All*, *Debits Only*, or *Credits Only* view states.
* **Conditional Color Engine:** Optional layout switch to instantly highlight debits in **Green** and credits in **Red**.
* **Indian Metric Ledger Totals:** Computes dynamic live balances for both total deposits and withdrawals matching current filters, beautifully formatted using the Indian numbering arrangement (e.g., `Rs. 1,00,00,000.00`).
* **Visible Sign Indicators:** Explicitly prefixes columns and items with permanent indicators (`-` for withdrawals and `+` for deposits).

---

## Setup and Installation

### 1. Prerequisites by Operating System

#### **Windows 10 / 11**
Tkinter comes bundled with Python on Windows. If you run into a `ModuleNotFoundError`, re-run your official Python installer wizard, select **Modify**, and make sure the box next to **"tcl/tk and IDLE"** is checked.

#### **Zorin OS / Ubuntu / Linux Mint**
Linux distributions separate graphical components from standard Python packages. Open your terminal window and run:
```bash
sudo apt update
sudo apt install python3-tk python3-pip python3-venv
```

2. Project Installation & Run Steps
Clone or navigate to your project directory, open your terminal/command prompt, and execute the following sequential commands:

# 1. Create a clean virtual environment
```bash
python3 -m venv venv
```
# 2. Activate the virtual environment
## On Windows:
```
venv\Scripts\activate
```
## On Zorin OS / Linux / macOS:
```
source venv/bin/activate
```
## 3. Upgrade your package manager
```
pip install --upgrade pip
```

## 4. Install required third-party libraries
```
pip install pandas tkinterdnd2
```

## 5. Execute the desktop app
```
python app.py
```
Compiling to a Standalone Application
If you want to package this Python code into an application binary executable that users can double-click to open without installing Python, follow these steps:

# 1. Install Compiler Tools
With your virtual environment still activated, install PyInstaller:

```bash
pip install pyinstaller
```
## 2. Compilation Commands
Crucial Rule: You must compile the binaries on their target operating systems. You cannot compile a Linux binary from Windows, or a Windows executable from Linux.

### For Windows 10 / 11
Run this command in the command prompt:

### DOS
```
pyinstaller --noconsole --onefile --collect-data tkinterdnd2 app1.py
```
Your independent app will be generated inside the newly created dist/ directory as app1.exe.

### For Zorin OS (Linux)
Run this command in the terminal:

```bash
pyinstaller --noconsole --onefile --collect-data tkinterdnd2 app1.py
```
Your independent app will be generated inside the newly created dist/ directory as a binary executable file named app1.

Creating Desktop Shortcuts
Windows 10 / 11
Navigate to your project's dist/ folder.

Right-click on app1.exe.

Select Send to -> Desktop (create shortcut).

Zorin OS (Linux)
Go to your Desktop environment screen, right-click, and make a new text document named StatementAnalyzer.desktop.

Open it with your text editor and paste the configuration properties below:
```
Ini, TOML
[Desktop Entry]
Version=1.0
Type=Application
Name=Account Statement Analyzer
Comment=Analyze Bank Statements
Exec=/absolute/path/to/your/project/dist/app1
Icon=utilities-terminal
Terminal=false
Categories=Office;Finance;
(Ensure you swap /absolute/path/to/your/project/dist/app1 with the exact folder layout mapping on your computer)
```
Save the document, right-click its desktop icon wrapper, and select "Allow Launching".