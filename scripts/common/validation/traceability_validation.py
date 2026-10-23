"""Validate traceability check."""

from validation_models import ValidationResult, ValidationStage


class TraceabilityValidation:
    def validate_traceability(self) -> ValidationResult:
        """Проверить связи REQ → Tests → Code."""
        print("\n🔍 Проверка трейсабилити...")
        errors = []
        warnings = []
        requirements_dir = self.project_root / "docs" / "requirements"
        if not requirements_dir.exists():
            return self._skipped_result("Директория requirements не найдена")
        req_files = list(requirements_dir.glob("REQ-*.md"))
        if not req_files:
            return self._skipped_result("Файлы требований REQ-*.md не найдены")
        for req_file in req_files:
            req_errors, req_warnings = self._validate_requirement(req_file)
            errors.extend(req_errors)
            warnings.extend(req_warnings)
        passed = len(errors) == 0
        message = (
            f"Трейсабилити проверена: {len(req_files)} требований"
            if passed
            else f"Найдено проблем с трейсабилити: {len(errors)}"
        )
        return ValidationResult(
            stage=ValidationStage.TRACEABILITY,
            passed=passed,
            message=message,
            details={"total_requirements": len(req_files), "checked_links": True},
            errors=errors,
            warnings=warnings,
        )

    def _validate_requirement(self, req_file):
        content = req_file.read_text(encoding="utf-8")
        req_id = req_file.stem
        errors = self._requirement_link_errors(req_id, content)
        warnings = self._acceptance_warnings(req_id, content)
        return errors, warnings

    @staticmethod
    def _requirement_link_errors(req_id, content):
        errors = []
        lines = content.splitlines()
        if not any("Tests:" in line or "Тесты:" in line for line in lines):
            errors.append(f"{req_id}: Нет ссылок на тесты")
        if not any("Modules:" in line or "Модули:" in line for line in lines):
            errors.append(f"{req_id}: Нет ссылок на модули")
        return errors

    @staticmethod
    def _acceptance_warnings(req_id, content):
        criteria = [line for line in content.splitlines() if line.startswith("- [")]
        if len(criteria) < 2:
            return [f"{req_id}: Мало критериев приёмки (<2)"]
        return []

    @staticmethod
    def _skipped_result(warning):
        return ValidationResult(
            stage=ValidationStage.TRACEABILITY,
            passed=True,
            message="Требования не найдены (пропущено)",
            warnings=[warning],
        )
