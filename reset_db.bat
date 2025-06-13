@echo off
setlocal ENABLEEXTENSIONS
title Reset bazy danych i migracji z adminem

echo === RESET MIGRACJI I BAZY DANYCH ===

REM Sprawdzenie venv
IF NOT DEFINED VIRTUAL_ENV (
    echo ⚠️  Venv nieaktywne.
    set /p CONTINUE="Kontynuować mimo to? (T/N): "
    IF /I NOT "%CONTINUE%"=="T" (
        echo ❌ Przerwano.
        exit /b
    )
)

REM Ścieżka do bazy
set DB_PATH=instance\dev.db

REM Usuwanie migracji
IF EXIST migrations (
    echo 🗑 Usuwanie folderu migrations...
    rmdir /S /Q migrations
)

REM Usuwanie bazy danych
IF EXIST %DB_PATH% (
    echo 🗑 Usuwanie bazy danych: %DB_PATH%
    del /Q %DB_PATH%
)

REM Tworzenie migracji
echo ⚙️  Inicjalizacja migracji...
flask db init

echo 📦 Tworzenie migracji...
flask db migrate -m "Reset: nowa baza danych"

echo 🚀 Wykonywanie migracji...
flask db upgrade

REM Tworzenie konta admina
echo.
echo 👤 Tworzenie konta administratora:
set /p ADMIN_NAME=Podaj nazwę admina:
flask create-admin %ADMIN_NAME%

echo.
echo ✅ Gotowe! Baza danych zresetowana, admin utworzony.
pause
endlocal
