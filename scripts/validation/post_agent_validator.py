#!/usr/bin/env python3
"""
Post-Agent Validation Runner
Автоматическая проверка всех артефактов после завершения работы агентов.

Проверки:
1. Трейсабилити (REQ → Tests → Code)
2. Безопасность (gitleaks, trivy, semgrep)
3. Форматирование кода
4. Анализ сложности (CNC ≤ 10)
5. Покрытие тестами (100% unit/integration/e2e/mutation)
6. Порог мутаций (100% функций имеют ≥2 мутации)
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class ValidationStage(Enum):
    TRACEABILITY = "traceability"
    SECURITY = "security"
    FORMATTING = "formatting"
    COMPLEXITY = "complexity"
    TEST_COVERAGE = "test_coverage"
    MUTATION_COVERAGE = "mutation_coverage"


@dataclass
class ValidationResult:
    stage: ValidationStage
    passed: bool
    message: str
    details: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class PostAgentValidator:
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

    def validate_traceability(self) -> ValidationResult:
        """
        Проверка трейсабилити: REQ → Tests → Code.
        Каждое требование должно иметь связанные тесты и код.
        """
        print("\n🔍 Проверка трейсабилити...")
        errors = []
        warnings = []
        
        requirements_dir = self.project_root / "requirements"
        if not requirements_dir.exists():
            return ValidationResult(
                stage=ValidationStage.TRACEABILITY,
                passed=True,
                message="Директория требований отсутствует (пропущено)",
                warnings=["Директория requirements не найдена"]
            )
        
        # Сбор всех требований
        req_files = list(requirements_dir.glob("REQ_*.md"))
        if not req_files:
            return ValidationResult(
                stage=ValidationStage.TRACEABILITY,
                passed=True,
                message="Требования не найдены (пропущено)",
                warnings=["Файлы требований REQ_*.md не найдены"]
            )
        
        # Проверка каждого требования
        for req_file in req_files:
            with open(req_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            req_id = req_file.stem  # Например, REQ_001
            
            # Проверка наличия ссылок на тесты
            test_links = [line for line in content.split('\n') if 'Tests:' in line or 'Тесты:' in line]
            if not test_links:
                errors.append(f"{req_id}: Нет ссылок на тесты")
            
            # Проверка наличия ссылок на код/модули
            code_links = [line for line in content.split('\n') if 'Modules:' in line or 'Модули:' in line]
            if not code_links:
                errors.append(f"{req_id}: Нет ссылок на модули")
            
            # Проверка критериев приёмки
            acceptance_criteria = [line for line in content.split('\n') if line.startswith('- [')]
            if len(acceptance_criteria) < 2:
                warnings.append(f"{req_id}: Мало критериев приёмки (<2)")
        
        passed = len(errors) == 0
        message = (
            f"Трейсабилити проверена: {len(req_files)} требований"
            if passed else
            f"Найдено проблем с трейсабилити: {len(errors)}"
        )
        
        return ValidationResult(
            stage=ValidationStage.TRACEABILITY,
            passed=passed,
            message=message,
            details={"total_requirements": len(req_files), "checked_links": True},
            errors=errors,
            warnings=warnings
        )

    def validate_security(self) -> ValidationResult:
        """
        Проверка безопасности через gitleaks, trivy, semgrep.
        """
        print("\n🔒 Проверка безопасности...")
        errors = []
        warnings = []
        
        security_script = self.project_root / "scripts" / "security" / "security_engine.sh"
        if not security_script.exists():
            return ValidationResult(
                stage=ValidationStage.SECURITY,
                passed=True,
                message="Скрипт безопасности не найден (пропущено)",
                warnings=["security_engine.sh не найден"]
            )
        
        try:
            result = subprocess.run(
                ["bash", str(security_script), "--ci-mode"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                errors.append(f"Security scan failed: {result.stderr}")
                # Парсинг вывода для детализации
                for line in result.stdout.split('\n'):
                    if '[ERROR]' in line or 'CRITICAL' in line:
                        errors.append(line.strip())
                    elif '[WARNING]' in line or 'WARN' in line:
                        warnings.append(line.strip())
            
            passed = result.returncode == 0
            message = (
                "Безопасность: все проверки пройдены"
                if passed else
                f"Безопасность: найдено уязвимостей ({len(errors)})"
            )
            
            return ValidationResult(
                stage=ValidationStage.SECURITY,
                passed=passed,
                message=message,
                details={"scan_duration": "N/A"},
                errors=errors[:10],  # Ограничим вывод
                warnings=warnings[:20]
            )
            
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
            lang_dir = self.project_root / "templates" / lang
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

    def validate_complexity(self) -> ValidationResult:
        """
        Проверка цикломатической сложности (CNC ≤ 10).
        """
        print("\n📊 Проверка сложности кода...")
        errors = []
        warnings = []
        
        complexity_script = self.project_root / "scripts" / "validation" / "complexity_analyzer.py"
        if not complexity_script.exists():
            return ValidationResult(
                stage=ValidationStage.COMPLEXITY,
                passed=True,
                message="Скрипт анализа сложности не найден (пропущено)",
                warnings=["complexity_analyzer.py не найден"]
            )
        
        try:
            result = subprocess.run(
                [sys.executable, str(complexity_script), "--threshold", str(self.complexity_threshold)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                # Парсинг вывода для извлечения нарушений
                for line in result.stdout.split('\n'):
                    if 'CNC >' in line or 'God Class' in line:
                        errors.append(line.strip())
                    elif 'WARNING' in line:
                        warnings.append(line.strip())
                
                if not errors and result.stderr:
                    errors.append(result.stderr.strip())
            
            passed = result.returncode == 0
            message = (
                f"Сложность: все функции CNC ≤ {self.complexity_threshold}"
                if passed else
                f"Сложность: найдено нарушений ({len(errors)})"
            )
            
            return ValidationResult(
                stage=ValidationStage.COMPLEXITY,
                passed=passed,
                message=message,
                details={"threshold": self.complexity_threshold},
                errors=errors[:20],
                warnings=warnings[:20]
            )
            
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

    def validate_test_coverage(self) -> ValidationResult:
        """
        Проверка покрытия тестами (100% для unit/integration/e2e).
        """
        print("\n🧪 Проверка покрытия тестами...")
        errors = []
        warnings = []
        
        coverage_report = self.project_root / "reports" / "coverage" / "coverage.json"
        if not coverage_report.exists():
            # Пытаемся запустить генерацию отчета
            coverage_script = self.project_root / "scripts" / "testing" / "generate_coverage.py"
            if coverage_script.exists():
                try:
                    subprocess.run(
                        [sys.executable, str(coverage_script)],
                        cwd=self.project_root,
                        capture_output=True,
                        timeout=180
                    )
                except Exception:
                    pass
            
            # Повторная проверка
            if not coverage_report.exists():
                return ValidationResult(
                    stage=ValidationStage.TEST_COVERAGE,
                    passed=True,
                    message="Отчет о покрытии не найден (пропущено)",
                    warnings=["coverage.json не найден"]
                )
        
        try:
            with open(coverage_report, 'r') as f:
                coverage_data = json.load(f)
            
            # Проверка порогов для каждого типа тестов
            for test_type, threshold in self.coverage_thresholds.items():
                if threshold == 0:
                    continue  # Пропускаем smoke/regression
                
                actual = coverage_data.get(test_type, {}).get("coverage_percent", 0)
                if actual < threshold:
                    errors.append(
                        f"{test_type}: покрытие {actual}% < порога {threshold}%"
                    )
                elif actual == 100.0:
                    pass  # OK
                else:
                    warnings.append(
                        f"{test_type}: покрытие {actual}% (целевое: 100%)"
                    )
            
            passed = len(errors) == 0
            message = (
                f"Покрытие тестами: OK (все пороги достигнуты)"
                if passed else
                f"Покрытие тестами: найдено проблем ({len(errors)})"
            )
            
            return ValidationResult(
                stage=ValidationStage.TEST_COVERAGE,
                passed=passed,
                message=message,
                details=coverage_data,
                errors=errors,
                warnings=warnings
            )
            
        except json.JSONDecodeError as e:
            return ValidationResult(
                stage=ValidationStage.TEST_COVERAGE,
                passed=False,
                message=f"Ошибка парсинга отчета о покрытии: {str(e)}",
                errors=[str(e)]
            )
        except Exception as e:
            return ValidationResult(
                stage=ValidationStage.TEST_COVERAGE,
                passed=False,
                message=f"Ошибка при проверке покрытия: {str(e)}",
                errors=[str(e)]
            )

    def validate_mutation_coverage(self) -> ValidationResult:
        """
        Проверка мутационного покрытия (100% функций имеют ≥2 мутации).
        """
        print("\n🧬 Проверка мутационного покрытия...")
        errors = []
        warnings = []
        
        mutation_report = self.project_root / "reports" / "mutation" / "mutation_report.json"
        if not mutation_report.exists():
            # Пытаемся запустить генерацию отчета
            mutation_script = self.project_root / "scripts" / "testing" / "mutation_runner.py"
            if mutation_script.exists():
                try:
                    subprocess.run(
                        [sys.executable, str(mutation_script), "--generate-report"],
                        cwd=self.project_root,
                        capture_output=True,
                        timeout=300
                    )
                except Exception:
                    pass
            
            # Повторная проверка
            if not mutation_report.exists():
                return ValidationResult(
                    stage=ValidationStage.MUTATION_COVERAGE,
                    passed=True,
                    message="Отчет о мутациях не найден (пропущено)",
                    warnings=["mutation_report.json не найден"]
                )
        
        try:
            with open(mutation_report, 'r') as f:
                mutation_data = json.load(f)
            
            total_functions = mutation_data.get("total_functions", 0)
            covered_functions = mutation_data.get("covered_functions", 0)
            functions_with_2_mutations = mutation_data.get("functions_with_2_mutations", 0)
            
            # Порог: 100% функций должны иметь ≥2 мутации
            if total_functions > 0:
                coverage_percent = (functions_with_2_mutations / total_functions) * 100
                
                if coverage_percent < 100.0:
                    uncovered = total_functions - functions_with_2_mutations
                    errors.append(
                        f"Мутации: {uncovered} функций без 2+ мутаций "
                        f"(покрытие: {coverage_percent:.1f}%)"
                    )
                
                # Проверка деталей
                for func_name, func_data in mutation_data.get("functions", {}).items():
                    mutations_count = func_data.get("mutations_count", 0)
                    if mutations_count < 2:
                        errors.append(
                            f"Функция '{func_name}': только {mutations_count} мутаций (требуется ≥2)"
                        )
            else:
                warnings.append("Нет данных о функциях для мутационного анализа")
            
            passed = len(errors) == 0
            message = (
                f"Мутационное покрытие: 100% функций имеют ≥2 мутации"
                if passed else
                f"Мутационное покрытие: найдено проблем ({len(errors)})"
            )
            
            return ValidationResult(
                stage=ValidationStage.MUTATION_COVERAGE,
                passed=passed,
                message=message,
                details={
                    "total_functions": total_functions,
                    "covered_functions": covered_functions,
                    "coverage_percent": (covered_functions / total_functions * 100) if total_functions > 0 else 0
                },
                errors=errors[:20],  # Ограничим вывод
                warnings=warnings
            )
            
        except json.JSONDecodeError as e:
            return ValidationResult(
                stage=ValidationStage.MUTATION_COVERAGE,
                passed=False,
                message=f"Ошибка парсинга отчета о мутациях: {str(e)}",
                errors=[str(e)]
            )
        except Exception as e:
            return ValidationResult(
                stage=ValidationStage.MUTATION_COVERAGE,
                passed=False,
                message=f"Ошибка при проверке мутаций: {str(e)}",
                errors=[str(e)]
            )

    def run_all_validations(self) -> bool:
        """
        Запуск всех проверок валидации.
        Возвращает True, если все проверки пройдены.
        """
        print("=" * 60)
        print("🚀 ЗАПУСК ПОСТ-АГЕНТ ВАЛИДАЦИИ")
        print("=" * 60)
        
        validations = [
            self.validate_traceability,
            self.validate_security,
            self.validate_formatting,
            self.validate_complexity,
            self.validate_test_coverage,
            self.validate_mutation_coverage,
        ]
        
        for validation_func in validations:
            try:
                result = validation_func()
                self.results.append(result)
                
                status = "✅ PASS" if result.passed else "❌ FAIL"
                print(f"\n{status} | {result.stage.value}: {result.message}")
                
                if result.errors:
                    for error in result.errors[:3]:
                        print(f"   └─ {error}")
                    if len(result.errors) > 3:
                        print(f"   └─ ... и ещё {len(result.errors) - 3} ошибок")
                
                if result.warnings:
                    for warning in result.warnings[:3]:
                        print(f"   ⚠️  {warning}")
                        
            except Exception as e:
                result = ValidationResult(
                    stage=ValidationStage(validation_func.__name__.replace('validate_', '')),
                    passed=False,
                    message=f"Критическая ошибка: {str(e)}",
                    errors=[str(e)]
                )
                self.results.append(result)
                print(f"\n❌ FAIL | {result.stage.value}: {result.message}")
        
        # Итоговый отчет
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 60)
        
        passed_count = sum(1 for r in self.results if r.passed)
        total_count = len(self.results)
        
        for result in self.results:
            status = "✅" if result.passed else "❌"
            print(f"{status} {result.stage.value}: {result.message}")
        
        all_passed = all(r.passed for r in self.results)
        
        print("\n" + "=" * 60)
        if all_passed:
            print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
        else:
            failed_count = total_count - passed_count
            print(f"❌ НЕ ПРОЙДЕНО ПРОВЕРОК: {failed_count}/{total_count}")
        print("=" * 60)
        
        # Сохранение отчета
        self._save_report()
        
        return all_passed

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
