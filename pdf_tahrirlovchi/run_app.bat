@echo off
chcp 65001 >nul 2>&1
title PDF Tahrirlovchi
color 0B

echo ============================================================
echo    PDF Tahrirlovchi - Ishga tushirish
echo ============================================================
echo.

:: Python tekshirish
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [XATO] Python topilmadi!
    echo Avval build.bat ni ishga tushiring.
    pause
    exit /b 1
)

:: streamlit tekshirish
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo [XATO] Kutubxonalar o'rnatilmagan!
    echo Avval build.bat ni ishga tushiring.
    pause
    exit /b 1
)

echo PDF Tahrirlovchi ishga tushirilmoqda...
echo.
echo Brauzer avtomatik ochiladi.
echo Agar ochilmasa, quyidagi manzilga o'ting:
echo    http://localhost:8501
echo.
echo Ilovani to'xtatish uchun bu oynani yoping yoki Ctrl+C bosing.
echo ============================================================
echo.

streamlit run app.py --server.headless=false --browser.gatherUsageStats=false

pause
