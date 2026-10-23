"""Validate security check."""

import subprocess
from validation_models import ValidationResult, ValidationStage


class SecurityValidation:
    def validate_security(self) -> ValidationResult:
        """Проверить безопасность через gitleaks, trivy, semgrep."""
        print("\n🔒 Проверка безопасности...")
        security_script = self.project_root / "scripts" / "security" / "security_engine.sh"
        if not security_script.exists():
            return ValidationResult(
                stage=ValidationStage.SECURITY,
                passed=False,
                message="Скрипт безопасности не найден",
                errors=["security_engine.sh не найден"],
            )
        try:
            result = self._run_scan(security_script)
            return self._result_from_process(result)
        except subprocess.TimeoutExpired:
            return ValidationResult(
                stage=ValidationStage.SECURITY,
                passed=False,
                message="Security scan timeout (>5 мин)",
                errors=["Превышено время выполнения сканирования"]
            )
        except Exception as e:
            return ValidationResult(
                stage=ValidationStage.SECURITY,
                passed=False,
                message=f"Ошибка при проверке безопасности: {str(e)}",
                errors=[str(e)]
            )

    def _run_scan(self, script):
        return subprocess.run(
            ["bash", str(script), "--ci-mode"],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            timeout=300,
        )

    def _result_from_process(self, process):
        errors, warnings = self._parse_findings(process.stdout)
        if process.returncode:
            errors.insert(0, f"Security scan failed: {process.stderr}")
        passed = process.returncode == 0
        message = "Безопасность: все проверки пройдены"
        if not passed:
            message = f"Безопасность: найдено уязвимостей ({len(errors)})"
        return ValidationResult(
            stage=ValidationStage.SECURITY,
            passed=passed,
            message=message,
            details={"scan_duration": "N/A"},
            errors=errors[:10],
            warnings=warnings[:20],
        )

    @staticmethod
    def _parse_findings(output):
        errors, warnings = [], []
        for line in output.splitlines():
            if "[ERROR]" in line or "CRITICAL" in line:
                errors.append(line.strip())
            elif "[WARNING]" in line or "WARN" in line:
                warnings.append(line.strip())
        return errors, warnings
