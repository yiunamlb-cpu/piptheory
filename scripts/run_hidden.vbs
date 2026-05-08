' Hidden-window wrapper for PowerShell.
' Task Scheduler running powershell.exe -WindowStyle Hidden still flashes
' a console for a fraction of a second because the hidden flag is applied
' after the process starts. wscript.exe + Run with WindowStyle=0 launches
' the child process invisibly from the kernel's perspective — no flash.
'
' Usage from a scheduled task action:
'   Program: wscript.exe
'   Args:    "C:\path\to\run_hidden.vbs" "C:\path\to\script.ps1"

If WScript.Arguments.Count < 1 Then
    WScript.Quit 1
End If

Dim shell, cmd, i
Set shell = CreateObject("WScript.Shell")

' Quote and forward all arguments to PowerShell as a -File invocation
cmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & WScript.Arguments(0) & """"
For i = 1 To WScript.Arguments.Count - 1
    cmd = cmd & " """ & WScript.Arguments(i) & """"
Next

' WindowStyle 0 = Hidden, second arg waits for completion (False = no wait)
shell.Run cmd, 0, False
