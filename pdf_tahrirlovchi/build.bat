@echo off
chcp 65001 >nul 2>&1
title PDF Tahrirlovchi - EXE Builder
color 0A

echo ============================================================
echo    PDF Tahrirlovchi - Avtomatik EXE Quruvchi
echo ============================================================
echo.

:: Python mavjudligini tekshirish
echo [1/5] Python tekshirilmoqda...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [XATO] Python topilmadi!
    echo Python 3.8+ o'rnatilgan bo'lishi kerak.
    echo https://www.python.org/downloads/ dan yuklab oling.
    echo O'rnatishda "Add Python to PATH" ni belgilang!
    pause
    exit /b 1
)
python --version
echo [OK] Python topildi.
echo.

:: pip mavjudligini tekshirish
echo [2/5] pip tekshirilmoqda...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [XATO] pip topilmadi! Python qayta o'rnating.
    pause
    exit /b 1
)
echo [OK] pip topildi.
echo.

:: pip yangilash
echo [3/5] pip yangilanmoqda...
python -m pip install --upgrade pip >nul 2>&1
echo [OK] pip yangilandi.
echo.

:: Kutubxonalarni o'rnatish
echo [4/5] Kutubxonalar o'rnatilmoqda...
echo     - streamlit o'rnatilmoqda...
python -m pip install streamlit>=1.28.0 >nul 2>&1
if %errorlevel% neq 0 (
    echo [XATO] streamlit o'rnatishda muammo!
    echo Internetga ulanishni tekshiring.
    pause
    exit /b 1
)
echo     - PyMuPDF o'rnatilmoqda...
python -m pip install PyMuPDF>=1.23.0 >nul 2>&1
if %errorlevel% neq 0 (
    echo [XATO] PyMuPDF o'rnatishda muammo!
    pause
    exit /b 1
)
echo     - python-docx o'rnatilmoqda...
python -m pip install python-docx>=1.1.0 >nul 2>&1
if %errorlevel% neq 0 (
    echo [XATO] python-docx o'rnatishda muammo!
    pause
    exit /b 1
)
echo     - pyinstaller o'rnatilmoqda...
python -m pip install pyinstaller>=6.0.0 >nul 2>&1
if %errorlevel% neq 0 (
    echo [XATO] pyinstaller o'rnatishda muammo!
    pause
    exit /b 1
)
echo [OK] Barcha kutubxonalar o'rnatildi.
echo.

:: EXE faylni qurish
echo [5/5] EXE fayl qurilmoqda (bu biroz vaqt olishi mumkin)...
echo.

:: PyInstaller bilan spec fayldan qurish
if exist "pdf_tahrirlovchi.spec" (
    echo     spec fayl topildi, undan foydalanilmoqda...
    python -m PyInstaller pdf_tahrirlovchi.spec --noconfirm
) else (
    echo     spec fayl topilmadi, standart sozlamalar bilan qurilmoqda...
    python -m PyInstaller --name "PDF_Tahrirlovchi" --onedir --noconfirm --clean ^
        --hidden-import=streamlit ^
        --hidden-import=streamlit.runtime ^
        --hidden-import=streamlit.runtime.scriptrunner ^
        --hidden-import=streamlit.web ^
        --hidden-import=fitz ^
        --hidden-import=pymupdf ^
        --hidden-import=docx ^
        --collect-all streamlit ^
        --collect-all streamlit_extras ^
        --copy-metadata streamlit ^
        app.py
)

if %errorlevel% neq 0 (
    echo.
    echo [XATO] EXE qurish muvaffaqiyatsiz tugadi!
    echo Xatolik ma'lumotlarini yuqorida ko'ring.
    echo.
    echo Mumkin yechimlar:
    echo   1. Antivirusni vaqtincha o'chiring
    echo   2. Administrator sifatida ishga tushiring
    echo   3. Python qayta o'rnating
    pause
    exit /b 1
)

echo.
echo ============================================================
echo    MUVAFFAQIYAT! EXE fayl tayyor!
echo ============================================================
echo.
echo EXE fayl joylashuvi:
echo    dist\PDF_Tahrirlovchi\
echo.
echo Ishga tushirish uchun:
echo    dist\PDF_Tahrirlovchi\run_app.bat ni bosing
echo.
echo ESLATMA: Ilovani ishga tushirish uchun dist\PDF_Tahrirlovchi
echo papkasidagi run_app.bat faylini ikki marta bosing.
echo Brauzer avtomatik ochiladi.
echo ============================================================

:: dist papkaga run_app.bat yaratish
if not exist "dist\PDF_Tahrirlovchi" mkdir "dist\PDF_Tahrirlovchi"

:: Asosiy fayllarni dist papkaga nusxalash
copy /Y app.py "dist\PDF_Tahrirlovchi\" >nul 2>&1
copy /Y pdf_engine.py "dist\PDF_Tahrirlovchi\" >nul 2>&1
copy /Y exporters.py "dist\PDF_Tahrirlovchi\" >nul 2>&1

:: run_app.bat yaratish
(
echo @echo off
echo chcp 65001 ^>nul 2^>^&1
echo title PDF Tahrirlovchi
echo echo PDF Tahrirlovchi ishga tushirilmoqda...
echo echo Brauzer avtomatik ochiladi. Agar ochilmasa, http://localhost:8501 ga o'ting.
echo echo.
echo echo Ilovani to'xtatish uchun bu oynani yoping.
echo streamlit run app.py --server.headless=false --browser.gatherUsageStats=false
echo pause
) > "dist\PDF_Tahrirlovchi\run_app.bat"

echo.
pause
