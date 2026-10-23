"""Validate test coverage check."""

import json
import subprocess
import sys
from validation_models import ValidationResult, ValidationStage


class TestCoverageValidation:
    def validate_test_coverage(self) -> ValidationResult:
        """Проверить покрытие тестами для обязательных suite."""
        print("\n🧪 Проверка покрытия тестами...")
        coverage_report = self.project_root / "reports" / "coverage" / "coverage.json"
        if not self._ensure_report(coverage_report):
            return self._missing_report_result()
        try:
            data = json.loads(coverage_report.read_text(encoding="utf-8"))
            errors, warnings = self._check_thresholds(data)
            return self._result(data, errors, warnings)
        except json.JSONDecodeError as e:
            return self._failure_result(f"Ошибка парсинга отчета о покрытии: {e}", e)
        except Exception as e:
            return self._failure_result(f"Ошибка при проверке покрытия: {e}", e)

    def _ensure_report(self, report):
        if report.exists():
            return True
        script = self.project_root / "scripts" / "testing" / "generate_coverage.py"
        if not script.exists():
            return False
        try:
            subprocess.run(
                [sys.executable, str(script)],
                cwd=self.project_root,
                capture_output=True,
                timeout=180,
                check=False,
            )
        except Exception:
            return report.exists()
        return report.exists()

    def _check_thresholds(self, data):
        errors, warnings = [], []
        for suite, threshold in self.coverage_thresholds.items():
            if threshold == 0:
                continue
            actual = data.get(suite, {}).get("coverage_percent", 0)
            if actual < threshold:
                errors.append(f"{suite}: покрытие {actual}% < порога {threshold}%")
            elif actual < 100.0:
                warnings.append(f"{suite}: покрытие {actual}% (целевое: 100%)")
        return errors, warnings

    @staticmethod
    def _result(data, errors, warnings):
        passed = not errors
        message = "Покрытие тестами: OK (все пороги достигнуты)"
        if not passed:
            message = f"Покрытие тестами: найдено проблем ({len(errors)})"
        return ValidationResult(
            stage=ValidationStage.TEST_COVERAGE,
            passed=passed,
            message=message,
            details=data,
            errors=errors,
            warnings=warnings,
        )

    @staticmethod
    def _missing_report_result():
        return ValidationResult(
            stage=ValidationStage.TEST_COVERAGE,
            passed=False,
            message="Отчет о покрытии не найден",
            errors=["coverage.json не найден"],
        )

    @staticmethod
    def _failure_result(message, error):
        return ValidationResult(
            stage=ValidationStage.TEST_COVERAGE,
            passed=False,
            message=message,
            errors=[str(error)],
        )
