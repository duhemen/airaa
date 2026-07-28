@echo off
chcp 65001 >nul
title AIRAA - AI Recording Angel Agentic v2.0

echo ============================================
echo 😇 AIRAA - AI Recording Angel Agentic v2.0
echo ============================================
echo.
echo 🔍 Memeriksa environment...

cd /d C:\airaa

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python tidak ditemukan!
    echo.
    echo ℹ️  Pastikan Python sudah terinstall dan ada di PATH.
    pause
    exit /b
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo ✅ Python %PYTHON_VER% ditemukan

REM Check pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Pip tidak ditemukan!
    pause
    exit /b
)
echo ✅ Pip ditemukan

REM Check requirements
echo.
echo 📦 Memeriksa dependencies...
pip list --format=freeze > installed.txt

REM Check Ollama
echo.
echo 🔍 Memeriksa Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Ollama tidak terdeteksi!
    echo.
    echo 💡 Pastikan Ollama sudah diinstall dan berjalan.
    echo    Download: https://ollama.com
    echo.
    echo 🔄 Menjalankan AIRAA dalam mode offline...
    echo    (Beberapa fitur seperti LLM akan dinonaktifkan)
    echo.
    timeout /t 2 >nul
    set OLLAMA_MODE=offline
) else (
    echo ✅ Ollama terdeteksi!
    
    REM Check models
    echo.
    echo 📦 Memeriksa model Ollama...
    curl -s http://localhost:11434/api/tags | find "nomic-embed-text" >nul
    if errorlevel 1 (
        echo ⚠️  Model nomic-embed-text tidak ditemukan!
        echo    Jalankan: ollama pull nomic-embed-text
    ) else (
        echo ✅ Model nomic-embed-text tersedia
    )
    
    curl -s http://localhost:11434/api/tags | find "qwen2.5:7b" >nul
    if errorlevel 1 (
        echo ⚠️  Model qwen2.5:7b-instruct tidak ditemukan!
        echo    Jalankan: ollama pull qwen2.5:7b-instruct
    ) else (
        echo ✅ Model qwen2.5:7b-instruct tersedia
    )
    set OLLAMA_MODE=online
)

REM Check dan buat direktori
echo.
echo 📁 Memeriksa direktori...
for %%d in (agent knowledge db logs audio config) do (
    if not exist "C:\airaa\%%d" (
        echo    📂 Membuat direktori: %%d
        mkdir "C:\airaa\%%d" 2>nul
    )
)
echo ✅ Semua direktori siap

REM Check settings.json
if not exist "C:\airaa\config\settings.json" (
    echo 📝 Membuat file settings.json default...
)

echo.
echo ============================================
echo 🚀 Menjalankan AIRAA...
echo ============================================
echo.

REM Jalankan AIRAA
python main.py

if errorlevel 1 (
    echo.
    echo ============================================
    echo ❌ AIRAA gagal dijalankan!
    echo ============================================
    echo.
    echo ℹ️  Periksa error di atas.
    echo.
    echo 💡 Tips troubleshooting:
    echo    1. Pastikan semua dependency terinstall:
    echo       pip install -r requirements.txt
    echo    2. Pastikan file settings.json valid
    echo    3. Cek log di folder logs/
    echo.
    pause
    exit /b
)

echo.
echo ============================================
echo 😇 AIRAA selesai. Sampai jumpa, Emen!
echo ============================================
pause