"""Validate formatting check."""

import subprocess
from validation_models import ValidationResult, ValidationStage


class FormattingValidation:
    def validate_formatting(self) -> ValidationResult:
        """
        Проверка форматирования кода для всех языков.
        """
        print("\n✨ Проверка форматирования...")
        errors = []
        warnings = []

        formatters = {
            "python": ["black", "--check", "--diff", "."],
            "javascript": ["prettier", "--check", "**/*.{js,ts,json}"],
            "rust": ["cargo", "fmt", "--check"],
            "go": ["gofmt", "-l", "."],
            "csharp": ["dotnet", "format", "--verify-no-changes"]
        }

        checked_languages = []

        for lang, cmd in formatters.items():
            lang_dir = self.project_root / "src" / "templates" / lang
            if not lang_dir.exists():
                continue

            try:
                # Проверяем наличие инструмента
                tool = cmd[0]
                check_result = subprocess.run(
                    ["which", tool],
                    capture_output=True,
                    text=True
                )

                if check_result.returncode != 0:
                    warnings.append(f"{lang}: инструмент {tool} не найден")
                    continue

                # Запускаем проверку форматирования
                result = subprocess.run(
                    cmd,
                    cwd=lang_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode != 0:
                    errors.append(f"{lang}: нарушения форматирования")
                    if result.stdout:
                        errors.append(f"  {result.stdout[:200]}")
                else:
                    checked_languages.append(lang)

            except Exception as e:
                warnings.append(f"{lang}: ошибка проверки ({str(e)})")

        passed = len(errors) == 0
        message = (
            f"Форматирование: OK ({len(checked_languages)} языков)"
            if passed else
            f"Форматирование: найдено нарушений ({len(errors)})"
        )

        return ValidationResult(
            stage=ValidationStage.FORMATTING,
            passed=passed,
            message=message,
            details={"checked_languages": checked_languages},
            errors=errors,
            warnings=warnings
        )
