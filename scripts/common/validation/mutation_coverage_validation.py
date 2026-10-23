"""Validate mutation coverage check."""

import json
import subprocess
import sys
from validation_models import ValidationResult, ValidationStage


class MutationCoverageValidation:
    def validate_mutation_coverage(self) -> ValidationResult:
        """Проверить наличие двух убитых мутаций для каждой функции."""
        print("\n🧬 Проверка мутационного покрытия...")
        mutation_report = self.project_root / "reports" / "mutation" / "mutation_report.json"
        if not mutation_report.exists() and not self._generate_report(mutation_report):
            return self._missing_report_result()
        try:
            return self._result_from_data(json.loads(mutation_report.read_text(encoding="utf-8")))
        except json.JSONDecodeError as e:
            return self._failure_result(f"Ошибка парсинга отчета о мутациях: {e}", e)
        except Exception as e:
            return self._failure_result(f"Ошибка при проверке мутаций: {e}", e)

    def _generate_report(self, report_path) -> bool:
        script = self.project_root / "scripts" / "testing" / "mutation_runner.py"
        if not script.exists():
            return False
        try:
            subprocess.run(
                [sys.executable, str(script), "--generate-report"],
                cwd=self.project_root,
                capture_output=True,
                timeout=300,
                check=False,
            )
        except Exception:
            return report_path.exists()
        return report_path.exists()

    def _result_from_data(self, data) -> ValidationResult:
        total = data.get("total_functions", 0)
        covered = data.get("functions_with_2_mutations", data.get("covered_functions", 0))
        errors = self._coverage_errors(data, total, covered)
        warnings = [] if total else ["Нет данных о функциях для мутационного анализа"]
        if not total:
            errors.append("Нет функций для обязательного мутационного анализа")
        passed = not errors
        message = "Мутационное покрытие: 100% функций имеют ≥2 мутации"
        if not passed:
            message = f"Мутационное покрытие: найдено проблем ({len(errors)})"
        return ValidationResult(
            stage=ValidationStage.MUTATION_COVERAGE,
            passed=passed,
            message=message,
            details={"total_functions": total, "covered_functions": covered, "coverage_percent": self._coverage(total, covered)},
            errors=errors[:20],
            warnings=warnings,
        )

    def _coverage_errors(self, data, total, covered):
        errors = []
        if total and covered < total:
            errors.append(f"Мутации: {total - covered} функций без 2+ мутаций (покрытие: {self._coverage(total, covered):.1f}%)")
        for name, details in data.get("functions", {}).items():
            count = details.get("mutations_count", 0)
            if count < 2:
                errors.append(f"Функция '{name}': только {count} мутаций (требуется ≥2)")
        return errors

    @staticmethod
    def _coverage(total, covered):
        return covered / total * 100 if total else 0

    @staticmethod
    def _missing_report_result():
        return ValidationResult(
            stage=ValidationStage.MUTATION_COVERAGE,
            passed=False,
            message="Отчет о мутациях не найден",
            errors=["mutation_report.json не найден"],
        )

    @staticmethod
    def _failure_result(message, error):
        return ValidationResult(
            stage=ValidationStage.MUTATION_COVERAGE,
            passed=False,
            message=message,
            errors=[str(error)],
        )
