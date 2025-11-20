@echo off
echo ========================================
echo Tambah Windows Defender Exclusion
echo ========================================
echo.
echo Script ini akan menambahkan folder dist ke exclusion list
echo Windows Defender agar aplikasi tidak diblokir.
echo.
echo CATATAN: Script ini memerlukan Administrator privileges
echo.
pause

echo.
echo Menambahkan exclusion...
echo.

REM Add exclusion for dist folder
powershell -Command "Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command \"Add-MpPreference -ExclusionPath \"\"%CD%\\dist\"\"\"' -Verb RunAs"

echo.
echo ========================================
echo Selesai!
echo ========================================
echo.
echo Folder yang ditambahkan ke exclusion:
echo %CD%\dist
echo.
echo Silakan rebuild aplikasi dengan menjalankan build.bat
echo.
pause
