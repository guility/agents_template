#!/usr/bin/env python3
"""Post-agent validation orchestration and command-line entry point."""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

_VALIDATION_DIR = str(Path(__file__).resolve().parent)
if _VALIDATION_DIR not in sys.path:
    sys.path.insert(0, _VALIDATION_DIR)

from validation_models import ValidationResult, ValidationStage
from traceability_validation import TraceabilityValidation
from security_validation import SecurityValidation
from formatting_validation import FormattingValidation
from complexity_validation import ComplexityValidation
from test_coverage_validation import TestCoverageValidation
from mutation_coverage_validation import MutationCoverageValidation


class PostAgentValidator(
    TraceabilityValidation,
    SecurityValidation,
    FormattingValidation,
    ComplexityValidation,
    TestCoverageValidation,
    MutationCoverageValidation,
):
    """Валидатор артефактов после работы агентов."""

    def __init__(self, project_root: Path, config: Optional[Dict] = None):
        self.project_root = project_root
        self.config = config or self._load_config()
        self.results: List[ValidationResult] = []

        # Пороги покрытия (100% для основных типов тестов)
        self.coverage_thresholds = {
            "unit": 100.0,
            "integration": 100.0,
            "e2e": 100.0,
            "mutation": 100.0,  # 100% функций должны иметь ≥2 мутации
            "smoke": 0.0,       # Smoke тесты - по усмотрению
            "regression": 0.0   # Регрессионные - по усмотрению
        }

        # Порог сложности
        self.complexity_threshold = 10


    def _load_config(self) -> Dict:
        """Загрузка конфигурации из файла."""
        config_path = self.project_root / ".validation_config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}


    def run_all_validations(self) -> bool:
        """Запустить проверки и сохранить итоговый отчёт."""
        print("=" * 60)
        print("🚀 ЗАПУСК ПОСТ-АГЕНТ ВАЛИДАЦИИ")
        print("=" * 60)
        for validation in [
            self.validate_traceability,
            self.validate_security,
            self.validate_formatting,
            self.validate_complexity,
            self.validate_test_coverage,
            self.validate_mutation_coverage,
        ]:
            self._run_validation(validation)
        self._print_summary()
        self._save_report()
        return all(result.passed for result in self.results)

    def _run_validation(self, validation):
        try:
            result = validation()
        except Exception as error:
            stage = ValidationStage(validation.__name__.replace("validate_", ""))
            result = ValidationResult(
                stage=stage,
                passed=False,
                message=f"Критическая ошибка: {error}",
                errors=[str(error)],
            )
        self.results.append(result)
        self._print_result(result)

    @staticmethod
    def _print_result(result):
        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"\n{status} | {result.stage.value}: {result.message}")
        for error in result.errors[:3]:
            print(f"   └─ {error}")
        if len(result.errors) > 3:
            print(f"   └─ ... и ещё {len(result.errors) - 3} ошибок")
        for warning in result.warnings[:3]:
            print(f"   ⚠️  {warning}")

    def _print_summary(self):
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 60)
        for result in self.results:
            status = "✅" if result.passed else "❌"
            print(f"{status} {result.stage.value}: {result.message}")
        all_passed = all(result.passed for result in self.results)
        print("\n" + "=" * 60)
        if all_passed:
            print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
        else:
            failed_count = sum(not result.passed for result in self.results)
            print(f"❌ НЕ ПРОЙДЕНО ПРОВЕРОК: {failed_count}/{len(self.results)}")
        print("=" * 60)


    def _save_report(self):
        """Сохранение отчета о валидации."""
        report_dir = self.project_root / "reports" / "validation"
        report_dir.mkdir(parents=True, exist_ok=True)

        report_data = {
            "timestamp": str(__import__('datetime').datetime.now().isoformat()),
            "results": [
                {
                    "stage": r.stage.value,
                    "passed": r.passed,
                    "message": r.message,
                    "details": r.details,
                    "errors": r.errors,
                    "warnings": r.warnings
                }
                for r in self.results
            ],
            "summary": {
                "total": len(self.results),
                "passed": sum(1 for r in self.results if r.passed),
                "failed": sum(1 for r in self.results if not r.passed)
            }
        }

        report_path = report_dir / "validation_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Отчет сохранен: {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Post-Agent Validation Runner"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("."),
        help="Корневая директория проекта"
    )
    parser.add_argument(
        "--stage",
        type=str,
        choices=[e.value for e in ValidationStage],
        help="Запустить только указанную проверку"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="console",
        choices=["console", "json"],
        help="Формат вывода"
    )

    args = parser.parse_args()

    validator = PostAgentValidator(args.project_root)

    if args.stage:
        # Запуск конкретной проверки
        stage_map = {
            "traceability": validator.validate_traceability,
            "security": validator.validate_security,
            "formatting": validator.validate_formatting,
            "complexity": validator.validate_complexity,
            "test_coverage": validator.validate_test_coverage,
            "mutation_coverage": validator.validate_mutation_coverage,
        }

        validation_func = stage_map.get(args.stage)
        if validation_func:
            result = validation_func()
            validator.results.append(result)

            if args.output == "json":
                print(json.dumps({
                    "stage": result.stage.value,
                    "passed": result.passed,
                    "message": result.message,
                    "errors": result.errors,
                    "warnings": result.warnings
                }, indent=2))
            else:
                status = "✅ PASS" if result.passed else "❌ FAIL"
                print(f"{status} | {result.stage.value}: {result.message}")
                if result.errors:
                    for error in result.errors:
                        print(f"   └─ {error}")

            sys.exit(0 if result.passed else 1)
    else:
        # Запуск всех проверок
        success = validator.run_all_validations()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
