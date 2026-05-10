' Hidden-window wrapper for the fetch_central_bank_statements.py script.
' Same pattern as dashboard_watchdog.vbs — wscript.exe runs windowless
' so no console flash on the scheduler tick. Uses the project's venv
' Python so requests/pypdf are available.

Option Explicit

Dim REPO, PYTHON, SCRIPT, LOG_PATH
REPO = "C:\Users\user\Downloads\claude hedgefund"
PYTHON = REPO & "\.venv\Scripts\python.exe"
SCRIPT = REPO & "\scripts\fetch_central_bank_statements.py"
LOG_PATH = REPO & "\logs\fetch_statements.log"

Dim shell, fso
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Make sure logs dir exists
Dim logsDir
logsDir = REPO & "\logs"
If Not fso.FolderExists(logsDir) Then fso.CreateFolder logsDir

' Append a timestamped run marker (the python script's own stdout is
' redirected into the same file so a single tail tells you what's been
' going on across runs).
Dim ts
ts = FormatDateTime(Now, 0)

Dim cmd
cmd = "cmd.exe /c """"" & PYTHON & """ """ & SCRIPT & """ >> """ & LOG_PATH & """ 2>&1"""
shell.Run cmd, 0, False
