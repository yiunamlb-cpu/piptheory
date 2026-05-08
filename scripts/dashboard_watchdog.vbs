' nam-hedgefund dashboard watchdog — pure VBScript, no PowerShell.
'
' Runs under wscript.exe which is genuinely windowless from the kernel's
' perspective, so no console flash on each scheduler tick. Earlier
' PowerShell-based version flashed briefly because PowerShell.exe is a
' console application — even with -WindowStyle Hidden, the host has to
' spawn a console process before the hide flag takes effect.
'
' What this does:
'   1. HTTP GET http://localhost:8501/api/run/status with a short timeout
'   2. If response is OK (200-499), dashboard is healthy — exit silently
'   3. Otherwise, log a line and launch run_dashboard.bat hidden via cmd
'
' Why HTTP check instead of port check: it tests whether the service is
' actually responding, not just whether something has the port bound.
' Catches uvicorn-hung-but-not-crashed scenarios.
'
' Logged failures (with timestamp) go to logs/watchdog.log. No log
' chatter when healthy — only fires when it actually has to act.

Option Explicit

Dim REPO, LOG_PATH, BAT_PATH, HEALTH_URL, REQUEST_TIMEOUT_MS
REPO = "C:\Users\user\Downloads\claude hedgefund"
LOG_PATH = REPO & "\logs\watchdog.log"
BAT_PATH = REPO & "\scripts\run_dashboard.bat"
HEALTH_URL = "http://localhost:8501/api/run/status"
REQUEST_TIMEOUT_MS = 3000

Dim shell, fso
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Make sure logs dir exists
Dim logsDir
logsDir = REPO & "\logs"
If Not fso.FolderExists(logsDir) Then fso.CreateFolder logsDir

Sub WriteLog(msg)
    Dim ts, f
    ts = FormatDateTime(Now, 0)
    On Error Resume Next
    Set f = fso.OpenTextFile(LOG_PATH, 8, True)
    If Not f Is Nothing Then
        f.WriteLine ts & " " & msg
        f.Close
    End If
    On Error Goto 0
End Sub

Function IsDashboardHealthy()
    Dim http, ok
    ok = False
    On Error Resume Next
    Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    If http Is Nothing Then
        ' Fallback to older XMLHTTP if ServerXMLHTTP isn't available
        Set http = CreateObject("MSXML2.XMLHTTP.6.0")
    End If
    If Not http Is Nothing Then
        http.SetTimeouts REQUEST_TIMEOUT_MS, REQUEST_TIMEOUT_MS, REQUEST_TIMEOUT_MS, REQUEST_TIMEOUT_MS
        http.Open "GET", HEALTH_URL, False
        http.Send
        If Err.Number = 0 Then
            ' Anything 2xx-4xx means the server is up and responding.
            ' 5xx might still be a working uvicorn returning an error,
            ' but we're cautious — only treat 200-499 as healthy.
            If http.Status >= 200 And http.Status < 500 Then
                ok = True
            End If
        End If
    End If
    On Error Goto 0
    IsDashboardHealthy = ok
End Function

' Main
If IsDashboardHealthy() Then
    ' Healthy. Exit silently so we don't fill the log on every tick.
    WScript.Quit 0
End If

WriteLog "Dashboard not responding at " & HEALTH_URL & ". Launching run_dashboard.bat..."

If Not fso.FileExists(BAT_PATH) Then
    WriteLog "FATAL: " & BAT_PATH & " not found"
    WScript.Quit 1
End If

' Launch the .bat hidden. WindowStyle 0 = hidden; third arg False = no wait.
' Wrapping with cmd /c so the child cmd's working directory inherits properly.
On Error Resume Next
shell.Run "cmd.exe /c """"" & BAT_PATH & """""", 0, False
If Err.Number <> 0 Then
    WriteLog "FAILED to start: " & Err.Description
    WScript.Quit 1
End If
On Error Goto 0

WriteLog "Launched. Subsequent ticks will verify."
WScript.Quit 0
