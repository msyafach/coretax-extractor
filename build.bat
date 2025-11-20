@echo off
echo ========================================
echo Building Coretax Extractor EXE
echo ========================================
echo.

REM Check if main file exists
if not exist coretax_extractor_flet.py (
    echo ERROR: coretax_extractor_flet.py tidak ditemukan!
    echo Pastikan file aplikasi utama ada.
    pause
    exit /b 1
)

echo Menggunakan file: coretax_extractor_flet.py
echo Mode: Folder Distribution (bukan single exe)
echo.

REM Check if pyinstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller tidak ditemukan. Menginstall...
    pip install pyinstaller
    echo.
)

REM Kill any running instance
echo Menutup aplikasi yang sedang berjalan...
taskkill /F /IM CoretaxExtractor.exe 2>nul
timeout /t 2 /nobreak >nul
echo.

REM Clean previous build
echo Membersihkan build sebelumnya...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

REM Check if icon exists
if not exist icon\app.ico (
    echo WARNING: Icon file not found at icon\app.ico
    echo Building without icon...
    echo.
) else (
    echo Using icon: icon\app.ico
    echo.
)

REM Check if logo exists
if not exist rsm.svg (
    echo WARNING: Logo file rsm.svg tidak ditemukan!
    echo Aplikasi akan menggunakan logo fallback.
    echo.
)

REM Build with spec file (creates folder distribution)
echo Membangun aplikasi...
echo Output: Folder distribusi dengan semua dependencies
echo.
pyinstaller build_exe.spec --clean --noconfirm
echo.

if exist dist\CoretaxExtractor\CoretaxExtractor.exe (
    echo ========================================
    echo Build berhasil!
    echo ========================================
    echo.
    echo Lokasi output: dist\CoretaxExtractor\
    echo Executable: dist\CoretaxExtractor\CoretaxExtractor.exe
    echo.
    echo ISI FOLDER DISTRIBUSI:
    echo - CoretaxExtractor.exe (executable utama^)
    echo - _internal\ (Python runtime dan dependencies^)
    echo - rsm.svg (file logo^)
    echo - db_manager.py (modul database^)
    echo.
    echo Anda dapat mendistribusikan seluruh folder CoretaxExtractor.
    echo User harus menjalankan CoretaxExtractor.exe dari dalam folder ini.
    echo.
    goto :end
)

echo ========================================
echo Build gagal!
echo ========================================
echo Silakan cek pesan error di atas.
echo.
echo Masalah umum:
echo 1. File coretax_extractor_flet.py tidak ada
echo 2. Dependencies kurang (jalankan: uv sync^)
echo 3. Masalah versi PyInstaller
echo.

:end

pause
