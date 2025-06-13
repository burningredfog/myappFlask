#!/bin/bash

echo "=== RESET MIGRACJI I BAZY DANYCH Z ADMINEM ==="

# Ścieżka do bazy danych
DB_PATH="instance/dev.db"

# Sprawdzenie czy venv aktywny
if [[ -z "$VIRTUAL_ENV" ]]; then
    read -p "⚠️  Środowisko venv nieaktywne. Kontynuować mimo to? (t/N): " CONTINUE
    if [[ "$CONTINUE" != "t" && "$CONTINUE" != "T" ]]; then
        echo "❌ Przerwano."
        exit 1
    fi
fi

# Usuwanie folderu migracji
if [ -d "migrations" ]; then
    echo "🗑 Usuwam migrations/"
    rm -rf migrations
fi

# Usuwanie bazy danych
if [ -f "$DB_PATH" ]; then
    echo "🗑 Usuwam bazę danych: $DB_PATH"
    rm -f "$DB_PATH"
fi

# Tworzenie nowych migracji
echo "⚙️  Inicjalizacja migracji..."
flask db init

echo "📦 Tworzenie migracji..."
flask db migrate -m "Reset: nowa baza danych"

echo "🚀 Wykonywanie migracji..."
flask db upgrade

# Tworzenie admina
echo ""
echo "👤 Tworzenie konta administratora:"
read -p "Podaj nazwę admina: " ADMIN_NAME
flask create-admin "$ADMIN_NAME"

echo ""
echo "✅ Gotowe! Baza danych zresetowana, migracje wykonane, admin utworzony."
