@echo off
rem Removes the two "Send to" entries. The program files and Python packages stay.
powershell -NoProfile -Command "$st=[Environment]::GetFolderPath('SendTo'); foreach($n in 'pdf2image','merge-image'){ Remove-Item -LiteralPath (Join-Path $st ($n+'.lnk')) -ErrorAction SilentlyContinue }"
echo Removed the "Send to" entries.
pause
