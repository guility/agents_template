#!/usr/bin/env bash
set -euo pipefail

# Скрипт проверки статуса workflow
# Валидирует, что переход между этапами разработки корректен

REQUIREMENTS_DIR="${1:-./requirements}"
DESIGN_DIR="${2:-./docs/design}"

echo "🔄 Проверка статуса workflow разработки"
echo ""

# Этап 1: Проверка требований
echo "=== Этап 1: Требования ==="
draft_count=0
approved_count=0
implemented_count=0

for file in "$REQUIREMENTS_DIR"/*.md; do
    [[ -f "$file" ]] || continue
    filename=$(basename "$file")
    [[ "$filename" == TEMPLATE* ]] && continue
    
    status=$(grep "^status:" "$file" | cut -d' ' -f2)
    case "$status" in
        draft) ((draft_count++)) ;;
        approved) ((approved_count++)) ;;
        implemented) ((implemented_count++)) ;;
        rejected) ;; # Игнорируем отклоненные
    esac
done

echo "  Draft: $draft_count"
echo "  Approved: $approved_count"
echo "  Implemented: $implemented_count"

if [[ "$draft_count" -gt 0 ]]; then
    echo "  ⚠️  Есть требования в статусе draft - они должны быть утверждены перед проектированием"
fi

# Этап 2: Проверка дизайн-документов для approved требований
echo ""
echo "=== Этап 2: Дизайн-документы ==="

missing_design=0
for file in "$REQUIREMENTS_DIR"/*.md; do
    [[ -f "$file" ]] || continue
    filename=$(basename "$file")
    [[ "$filename" == TEMPLATE* ]] && continue
    
    status=$(grep "^status:" "$file" | cut -d' ' -f2)
    req_id=$(grep "^id:" "$file" | cut -d' ' -f2)
    
    if [[ "$status" == "approved" || "$status" == "implemented" ]]; then
        # Проверяем наличие дизайн-документа
        design_file=$(find "$DESIGN_DIR" -name "*${req_id}*" 2>/dev/null | head -1)
        if [[ -z "$design_file" ]]; then
            echo "  ❌ Для требования $req_id ($status) не найден дизайн-документ"
            ((missing_design++))
        else
            # Проверяем статус дизайн-документа
            if ! grep -q "^status: \(draft\|approved\|implemented\)$" "$design_file"; then
                echo "  ⚠️  Дизайн-документ для $req_id не имеет корректного статуса"
            fi
        fi
    fi
done

if [[ "$missing_design" -eq 0 ]]; then
    echo "  ✅ Все утвержденные требования имеют дизайн-документы"
else
    echo "  ❌ Отсутствуют дизайн-документы для $missing_design требований"
fi

# Этап 3: Проверка тестов
echo ""
echo "=== Этап 3: Тесты ==="

tests_dir="./tests"
if [[ -d "$tests_dir" ]]; then
    unit_count=$(find "$tests_dir/unit" -type f 2>/dev/null | wc -l)
    integration_count=$(find "$tests_dir/integration" -type f 2>/dev/null | wc -l)
    e2e_count=$(find "$tests_dir/e2e" -type f 2>/dev/null | wc -l)
    
    echo "  Unit тестов: $unit_count"
    echo "  Integration тестов: $integration_count"
    echo "  E2E тестов: $e2e_count"
    
    if [[ "$implemented_count" -gt 0 && "$unit_count" -eq 0 ]]; then
        echo "  ⚠️  Есть реализованные требования, но нет unit тестов"
    fi
else
    echo "  ⚠️  Директория тестов не найдена"
fi

# Этап 4: Проверка покрытия мутационными тестами
echo ""
echo "=== Этап 4: Мутационное тестирование ==="

mutation_dir="$tests_dir/mutation"
if [[ -d "$mutation_dir" ]]; then
    mutation_count=$(find "$mutation_dir" -type f 2>/dev/null | wc -l)
    echo "  Мутационных тестов: $mutation_count"
else
    echo "  ℹ️  Директория мутационных тестов не найдена (будет создана при необходимости)"
fi

echo ""
echo "=== Итоговый статус ==="

if [[ "$draft_count" -eq 0 && "$missing_design" -eq 0 ]]; then
    echo "✅ Workflow валиден - можно продолжать разработку"
    exit 0
else
    echo "❌ Обнаружены проблемы в workflow"
    echo "   - Требований в draft: $draft_count"
    echo "   - Отсутствующих дизайн-документов: $missing_design"
    exit 1
fi
