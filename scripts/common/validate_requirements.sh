#!/usr/bin/env bash
set -euo pipefail

# Скрипт валидации требований
# Проверяет, что все файлы в /requirements соответствуют формату

REQUIREMENTS_DIR="${1:-./requirements}"
ERRORS=0

echo "🔍 Валидация требований в директории: $REQUIREMENTS_DIR"

if [[ ! -d "$REQUIREMENTS_DIR" ]]; then
    echo "❌ Директория требований не найдена: $REQUIREMENTS_DIR"
    exit 1
fi

# Находим все .md файлы кроме шаблонов
for file in "$REQUIREMENTS_DIR"/*.md; do
    [[ -f "$file" ]] || continue
    filename=$(basename "$file")
    
    # Пропускаем шаблоны
    if [[ "$filename" == TEMPLATE* ]]; then
        continue
    fi
    
    echo "Проверка: $filename"
    
    # Проверка наличия front matter
    if ! head -1 "$file" | grep -q "^---$"; then
        echo "  ❌ Отсутствует front matter (должен начинаться с ---)"
        ((ERRORS++))
        continue
    fi
    
    # Проверка обязательных полей
    if ! grep -q "^id: REQ-[0-9]\+" "$file"; then
        echo "  ❌ Отсутствует или некорректное поле 'id' (должно быть REQ-XXX)"
        ((ERRORS++))
    fi
    
    if ! grep -q "^title: .\+" "$file"; then
        echo "  ❌ Отсутствует поле 'title'"
        ((ERRORS++))
    fi
    
    if ! grep -q "^status: \(draft\|approved\|implemented\|rejected\)$" "$file"; then
        echo "  ❌ Отсутствует или некорректное поле 'status' (draft|approved|implemented|rejected)"
        ((ERRORS++))
    fi
    
    # Проверка наличия разделов
    if ! grep -q "^## Описание" "$file"; then
        echo "  ❌ Отсутствует раздел '## Описание'"
        ((ERRORS++))
    fi
    
    if ! grep -q "^## Критерии приемки" "$file"; then
        echo "  ❌ Отсутствует раздел '## Критерии приемки'"
        ((ERRORS++))
    fi
    
    # Проверка на дублирование ID
    id=$(grep "^id:" "$file" | cut -d' ' -f2)
    duplicate_files=$(grep -l "^id: $id$" "$REQUIREMENTS_DIR"/*.md 2>/dev/null | wc -l)
    if [[ "$duplicate_files" -gt 1 ]]; then
        echo "  ❌ Обнаружено дублирование ID: $id"
        ((ERRORS++))
    fi
    
    # Проверка ссылок на связанные требования
    if grep -q "^related:" "$file"; then
        related=$(grep "^related:" "$file" | sed 's/related: \[//' | sed 's/\]//')
        if [[ -n "$related" && "$related" != " " ]]; then
            for req_id in $(echo "$related" | tr ',' '\n' | tr -d ' '); do
                if ! grep -q "^id: $req_id$" "$REQUIREMENTS_DIR"/*.md; then
                    echo "  ⚠️  Ссылка на несуществующее требование: $req_id"
                fi
            done
        fi
    fi
done

echo ""
if [[ "$ERRORS" -eq 0 ]]; then
    echo "✅ Все требования валидны"
    exit 0
else
    echo "❌ Найдено ошибок: $ERRORS"
    exit 1
fi
