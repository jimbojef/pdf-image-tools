@echo off
rem Run once (safe to run again): installs PyMuPDF and Pillow and adds
rem "pdf2image" and "merge-image" to the Explorer right-click menu "Send to".
rem Only changes your user profile, no admin rights needed.
py -m pip install --user -r "%~dp0requirements.txt"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$d='%~dp0'; $st=[Environment]::GetFolderPath('SendTo'); $pyw=(Get-Command pyw.exe -ErrorAction Stop).Source; $sh=New-Object -ComObject WScript.Shell; $q=[char]34; foreach($n in 'pdf2image','merge-image'){ $s=$sh.CreateShortcut((Join-Path $st ($n+'.lnk'))); $s.TargetPath=$pyw; $s.Arguments=$q+(Join-Path $d ($n+'.pyw'))+$q; $s.WorkingDirectory=$d; $s.Save() }"
echo.
echo Done. Right-click files, then "Send to", then "pdf2image" or "merge-image".
pause
