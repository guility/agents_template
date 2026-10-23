"""Validate complexity check."""

import subprocess
import sys
from validation_models import ValidationResult, ValidationStage


class ComplexityValidation:
    def validate_complexity(self) -> ValidationResult:
        """Проверить цикломатическую сложность (CNC ≤ 10)."""
        print("\n📊 Проверка сложности кода...")
        complexity_script = self.project_root / "scripts" / "testing" / "complexity_analyzer.py"
        if not complexity_script.exists():
            return ValidationResult(
                stage=ValidationStage.COMPLEXITY,
                passed=False,
                message="Скрипт анализа сложности не найден",
                errors=["complexity_analyzer.py не найден"],
            )

        try:
            result = self._run_analyzer(complexity_script)
            return self._result_from_process(result)
        except subprocess.TimeoutExpired:
            return ValidationResult(
                stage=ValidationStage.COMPLEXITY,
                passed=False,
                message="Анализ сложности timeout (>2 мин)",
                errors=["Превышено время выполнения анализа"]
            )
        except Exception as e:
            return ValidationResult(
                stage=ValidationStage.COMPLEXITY,
                passed=False,
                message=f"Ошибка при анализе сложности: {str(e)}",
                errors=[str(e)]
            )

    def _run_analyzer(self, script):
        return subprocess.run(
            [sys.executable, str(script), "--threshold", str(self.complexity_threshold)],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            timeout=120,
        )

    def _result_from_process(self, process) -> ValidationResult:
        errors, warnings = self._parse_output(process)
        passed = process.returncode == 0
        message = (
            f"Сложность: все функции CNC ≤ {self.complexity_threshold}"
            if passed
            else f"Сложность: найдено нарушений ({len(errors)})"
        )
        return ValidationResult(
            stage=ValidationStage.COMPLEXITY,
            passed=passed,
            message=message,
            details={"threshold": self.complexity_threshold},
            errors=errors[:20],
            warnings=warnings[:20],
        )

    @staticmethod
    def _parse_output(process):
        errors, warnings = [], []
        if process.returncode == 0:
            return errors, warnings
        for line in process.stdout.splitlines():
            if "CNC >" in line or "God Class" in line:
                errors.append(line.strip())
            elif "WARNING" in line:
                warnings.append(line.strip())
        if not errors and process.stderr:
            errors.append(process.stderr.strip())
        return errors, warnings
