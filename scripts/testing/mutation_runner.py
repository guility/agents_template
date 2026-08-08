#!/usr/bin/env python3
"""
Mutation Test Runner
Генерирует минимум 2 мутации на каждую функцию и проверяет, что тесты их обнаруживают.

Порог покрытия: 100% функций должны иметь не менее 2 мутаций.
"""

import argparse
import json
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class MutationType(Enum):
    """Типы мутаций."""

    RETURN_VALUE = "return_value"
    CONDITIONAL_NEGATION = "conditional_negation"
    ARITHMETIC_OPERATOR = "arithmetic_operator"
    BOOLEAN_LITERAL = "boolean_literal"
    EXCEPTION_SUPPRESSION = "exception_suppression"
    LOOP_BOUNDARY = "loop_boundary"


@dataclass
class FunctionInfo:
    """Информация о функции."""

    name: str
    file_path: str
    line_start: int
    line_end: int
    language: str
    mutations_generated: int = 0
    mutations_killed: int = 0


@dataclass
class MutationResult:
    """Результат мутационного теста."""

    function_name: str
    mutation_type: MutationType
    mutation_id: str
    created: bool
    killed: bool
    language: str = ""
    file_path: str = ""
    original_source: Optional[str] = None
    mutated_source: Optional[str] = None
    test_that_killed: Optional[str] = None
    error_message: Optional[str] = None


class MutationRunner:
    """Запуск мутационных тестов."""

    def __init__(self, project_root: Path, config: Optional[Dict] = None):
        self.project_root = project_root
        self.config = config or self._load_config()
        self.results: List[MutationResult] = []
        self.functions: Dict[str, FunctionInfo] = {}
        self._baseline_errors: Dict[str, Optional[str]] = {}

        # Порог: 100% функций должны иметь не менее 2 мутаций
        self.mutation_threshold = 2
        self.coverage_threshold = 100.0
        self.mutation_score_threshold = 100.0

    def _load_config(self) -> Dict:
        """Загрузка конфигурации."""
        config_path = self.project_root / ".mutation_config.json"
        if config_path.exists():
            with open(config_path, "r") as f:
                return json.load(f)
        return {}

    def discover_functions(self, language: str = "python") -> List[FunctionInfo]:
        """Обнаружение функций в коде."""
        functions = []

        if language == "python":
            functions = self._discover_python_functions()
        elif language in ("javascript", "nodejs"):
            functions = self._discover_js_functions()
        elif language == "rust":
            functions = self._discover_rust_functions()
        elif language == "go":
            functions = self._discover_go_functions()
        elif language == "csharp":
            functions = self._discover_csharp_functions()

        return functions

    def _discover_python_functions(self) -> List[FunctionInfo]:
        """Обнаружение функций Python."""
        functions = []
        src_dir = self.project_root / "templates" / "python" / "src"

        if not src_dir.exists():
            return functions

        for py_file in src_dir.rglob("*.py"):
            if "test" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                current_func = None

                for i, line in enumerate(lines):
                    stripped = line.lstrip()

                    if stripped.startswith("def "):
                        func_name = stripped[4:].split("(")[0]

                        if current_func:
                            current_func.line_end = i

                        current_func = FunctionInfo(
                            name=func_name, file_path=str(py_file), line_start=i + 1, line_end=i + 1, language="python"
                        )
                        functions.append(current_func)

                if current_func and lines:
                    current_func.line_end = len(lines)

            except Exception as e:
                print(f"[WARN] Ошибка парсинга {py_file}: {e}")

        return functions

    def _discover_js_functions(self) -> List[FunctionInfo]:
        return self._generic_function_discovery("nodejs", ["js", "ts"])

    def _discover_rust_functions(self) -> List[FunctionInfo]:
        return self._generic_function_discovery("rust", ["rs"])

    def _discover_go_functions(self) -> List[FunctionInfo]:
        return self._generic_function_discovery("go", ["go"])

    def _discover_csharp_functions(self) -> List[FunctionInfo]:
        return self._generic_function_discovery("csharp", ["cs"])

    def _generic_function_discovery(self, language: str, extensions: List[str]) -> List[FunctionInfo]:
        """Универсальное обнаружение функций."""
        functions = []
        src_dir = self.project_root / "templates" / language / "src"

        if not src_dir.exists():
            return functions

        for ext in extensions:
            for code_file in src_dir.rglob(f"*.{ext}"):
                if "test" in str(code_file):
                    continue

                try:
                    with open(code_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if any(kw in line for kw in ["fn ", "function ", "func ", "public ", "private "]):
                            func_name = f"func_{language}_{i}"
                            functions.append(
                                FunctionInfo(
                                    name=func_name,
                                    file_path=str(code_file),
                                    line_start=i + 1,
                                    line_end=min(i + 20, len(lines)),
                                    language=language,
                                )
                            )
                except Exception as e:
                    print(f"[WARN] Ошибка парсинга {code_file}: {e}")

        return functions

    def _build_mutation(
        self,
        func: FunctionInfo,
        mutation_type: MutationType,
        suffix: str,
        pattern: str,
        replacement,
    ) -> Optional[MutationResult]:
        """Create a mutation containing the complete original and changed file."""
        file_path = Path(func.file_path)
        original = file_path.read_text(encoding="utf-8")
        lines = original.splitlines(keepends=True)
        start = max(func.line_start - 1, 0)
        end = min(func.line_end, len(lines))
        segment = "".join(lines[start:end])
        mutated_segment, count = re.subn(pattern, replacement, segment, count=1, flags=re.MULTILINE)
        if count == 0 or mutated_segment == segment:
            return None

        mutated = "".join(lines[:start]) + mutated_segment + "".join(lines[end:])
        return MutationResult(
            function_name=func.name,
            mutation_type=mutation_type,
            mutation_id=f"{func.name}_{suffix}",
            created=True,
            killed=False,
            language=func.language,
            file_path=str(file_path),
            original_source=original,
            mutated_source=mutated,
        )

    def generate_mutations(self, func: FunctionInfo) -> List[MutationResult]:
        """Generate real source mutations for one function."""
        strategies = (
            self._mutate_return_value,
            self._mutate_conditional,
            self._mutate_arithmetic,
            self._mutate_boolean,
        )
        mutations = [mutation for strategy in strategies if (mutation := strategy(func))]
        created = mutations[: self.mutation_threshold]
        while len(created) < self.mutation_threshold:
            created.append(
                MutationResult(
                    function_name=func.name,
                    mutation_type=MutationType.RETURN_VALUE,
                    mutation_id=f"{func.name}_missing_{len(created)}",
                    created=False,
                    killed=False,
                    language=func.language,
                    file_path=func.file_path,
                    error_message="No suitable source expression for a real mutation",
                )
            )
        func.mutations_generated = sum(mutation.created for mutation in created)
        return created

    def _mutate_return_value(self, func: FunctionInfo) -> Optional[MutationResult]:
        pattern = r"^(?P<indent>[ \t]*)return[ \t]+(?P<expr>[^\n#]+)(?P<comment>[ \t]*(?:#.*)?)$"

        def negate_return(match):
            expression = match.group("expr").strip()
            return f'{match.group("indent")}return not ({expression}){match.group("comment")}'

        return self._build_mutation(func, MutationType.RETURN_VALUE, "return", pattern, negate_return)

    def _mutate_conditional(self, func: FunctionInfo) -> Optional[MutationResult]:
        operators = {"==": "!=", "!=": "==", ">=": "<", "<=": ">", ">": "<=", "<": ">="}
        pattern = r"(?P<left>[\w.)\]]+)\s*(?P<op>==|!=|>=|<=|>|<)\s*(?P<right>[\w.(\[\]-]+)"

        def replace_operator(match):
            return f'{match.group("left")} {operators[match.group("op")]} {match.group("right")}'

        return self._build_mutation(func, MutationType.CONDITIONAL_NEGATION, "conditional", pattern, replace_operator)

    def _mutate_arithmetic(self, func: FunctionInfo) -> Optional[MutationResult]:
        operators = {"+": "-", "-": "+", "*": "/", "/": "*"}
        pattern = r"(?P<left>[\w.)\]]+)\s+(?P<op>[+*/-])\s+(?P<right>[\w.(\[\]-]+)"

        def replace_operator(match):
            return f'{match.group("left")} {operators[match.group("op")]} {match.group("right")}'

        return self._build_mutation(func, MutationType.ARITHMETIC_OPERATOR, "arithmetic", pattern, replace_operator)

    def _mutate_boolean(self, func: FunctionInfo) -> Optional[MutationResult]:
        values = {"True": "False", "False": "True", "true": "false", "false": "true"}
        return self._build_mutation(
            func,
            MutationType.BOOLEAN_LITERAL,
            "boolean",
            r"\b(True|False|true|false)\b",
            lambda match: values[match.group(0)],
        )

    def _test_command(self, language: str) -> List[str]:
        configured = self.config.get("test_commands", {}).get(language)
        if configured:
            return shlex.split(configured) if isinstance(configured, str) else list(configured)
        defaults = {
            "python": [sys.executable, "-m", "pytest"],
            "nodejs": ["pnpm", "test", "--", "--runInBand"],
            "rust": ["cargo", "test", "--all-features"],
            "go": ["go", "test", "./..."],
            "csharp": ["dotnet", "test"],
        }
        return defaults[language]

    def _project_directory(self, language: str) -> Path:
        configured = self.config.get("project_directories", {}).get(language)
        return self.project_root / (configured or f"templates/{language}")

    def _execute_tests(self, language: str):
        command = self._test_command(language)
        try:
            result = subprocess.run(
                command,
                cwd=self._project_directory(language),
                capture_output=True,
                text=True,
                timeout=int(self.config.get("test_timeout_seconds", 120)),
            )
            return result.returncode, result.stdout + result.stderr, None
        except (OSError, subprocess.TimeoutExpired) as error:
            return None, "", str(error)

    def _baseline_error(self, language: str) -> Optional[str]:
        if language not in self._baseline_errors:
            return_code, output, error = self._execute_tests(language)
            if error or return_code != 0:
                details = error or output[-1000:]
                self._baseline_errors[language] = f"Baseline tests failed: {details}"
            else:
                self._baseline_errors[language] = None
        return self._baseline_errors[language]

    def run_mutation_tests(self, mutation: MutationResult) -> bool:
        """Apply one mutation, execute tests, and restore the original source."""
        if not mutation.created or not mutation.mutated_source:
            return False
        baseline_error = self._baseline_error(mutation.language)
        if baseline_error:
            mutation.error_message = baseline_error
            return False

        file_path = Path(mutation.file_path)
        if file_path.read_text(encoding="utf-8") != mutation.original_source:
            mutation.error_message = "Source changed after mutation generation"
            return False

        try:
            file_path.write_text(mutation.mutated_source, encoding="utf-8")
            return_code, output, error = self._execute_tests(mutation.language)
            if error:
                mutation.error_message = error
                return False
            mutation.test_that_killed = " ".join(self._test_command(mutation.language)) if return_code else None
            if return_code == 0:
                mutation.error_message = f"Mutation survived. Test output: {output[-500:]}"
            return return_code != 0
        finally:
            file_path.write_text(mutation.original_source or "", encoding="utf-8")

    def run_all_mutations(self, languages: Optional[List[str]] = None) -> Dict:
        """Запуск всех мутационных тестов."""
        print("=" * 60)
        print("ЗАПУСК МУТАЦИОННОГО ТЕСТИРОВАНИЯ")
        print("=" * 60)
        languages = languages or ["python", "nodejs", "rust", "go", "csharp"]
        all_functions = self._discover_all_functions(languages)
        if not all_functions:
            print("\n[WARN] Функции не найдены")
            return self._generate_empty_report()

        print(f"\nВсего функций: {len(all_functions)}")
        print(f"Требуется мутаций на функцию: >= {self.mutation_threshold}")
        total_mutations, killed_mutations, covered_functions = self._mutation_totals(all_functions)
        coverage_percent = covered_functions / len(all_functions) * 100
        mutation_score = killed_mutations / total_mutations * 100 if total_mutations else 0
        threshold_passed = self._threshold_passed(total_mutations, coverage_percent, mutation_score)
        self._print_mutation_summary(
            all_functions,
            covered_functions,
            total_mutations,
            killed_mutations,
            coverage_percent,
            mutation_score,
            threshold_passed,
        )
        report = self._create_report(
            all_functions,
            covered_functions,
            total_mutations,
            killed_mutations,
            coverage_percent,
            mutation_score,
            threshold_passed,
        )
        self._save_report(report)
        return report

    def _discover_all_functions(self, languages: List[str]) -> List[FunctionInfo]:
        """Discover functions and show counts for each requested language."""
        all_functions = []
        for language in languages:
            functions = self.discover_functions(language)
            all_functions.extend(functions)
            print(f"\n{language.upper()}: найдено {len(functions)} функций")
        return all_functions

    def _mutation_totals(self, functions: List[FunctionInfo]):
        """Execute real mutations and return aggregate counters."""
        totals = [self._run_function_mutations(function) for function in functions]
        return tuple(sum(values) for values in zip(*totals))

    def _run_function_mutations(self, function: FunctionInfo):
        """Execute all generated mutations for one function."""
        mutations = self.generate_mutations(function)
        created = [mutation for mutation in mutations if mutation.created]
        killed = 0
        self.results.extend(mutations)
        for mutation in created:
            mutation.killed = self.run_mutation_tests(mutation)
            killed += int(mutation.killed)
        function.mutations_killed = killed
        covered = int(function.mutations_generated >= self.mutation_threshold)
        return len(created), killed, covered

    def _threshold_passed(self, total: int, coverage: float, score: float) -> bool:
        """Require both complete mutation coverage and a perfect mutation score."""
        return total > 0 and coverage >= self.coverage_threshold and score >= self.mutation_score_threshold

    def _print_mutation_summary(
        self,
        functions,
        covered,
        total,
        killed,
        coverage,
        score,
        threshold_passed,
    ) -> None:
        """Print aggregate mutation statistics."""
        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТЫ МУТАЦИОННОГО ТЕСТИРОВАНИЯ")
        print("=" * 60)
        print(f"Всего функций: {len(functions)}")
        print(f"Функций с >= {self.mutation_threshold} мутациями: {covered}")
        print(f"Покрытие мутациями: {coverage:.1f}%")
        print(f"Всего мутаций создано: {total}")
        print(f"Мутаций убито: {killed}")
        print(f"Mutation Score: {score:.1f}%")
        print("\n" + "=" * 60)
        if threshold_passed:
            print(f"[PASS] ПОРОГ ДОСТИГНУТ: {coverage:.1f}% >= {self.coverage_threshold}%")
        else:
            print(f"[FAIL] ПОРОГ НЕ ДОСТИГНУТ: coverage={coverage:.1f}%, score={score:.1f}%")
        print("=" * 60)

    def _create_report(
        self,
        functions,
        covered,
        total,
        killed,
        coverage,
        score,
        threshold_passed,
    ) -> Dict:
        """Build the machine-readable mutation report."""
        return {
            "timestamp": str(__import__("datetime").datetime.now().isoformat()),
            "total_functions": len(functions),
            "covered_functions": covered,
            "functions_with_2_mutations": covered,
            "coverage_percent": coverage,
            "total_mutations": total,
            "killed_mutations": killed,
            "mutation_score": score,
            "threshold_required": self.mutation_threshold,
            "coverage_threshold": self.coverage_threshold,
            "mutation_score_threshold": self.mutation_score_threshold,
            "threshold_passed": threshold_passed,
            "functions": {
                func.name: {
                    "file": func.file_path,
                    "language": func.language,
                    "mutations_count": func.mutations_generated,
                    "mutations_killed": func.mutations_killed,
                }
                for func in functions
            },
            "mutations": [
                {
                    "function": m.function_name,
                    "type": m.mutation_type.value,
                    "id": m.mutation_id,
                    "created": m.created,
                    "killed": m.killed,
                    "test": m.test_that_killed,
                    "error": m.error_message,
                }
                for m in self.results
            ],
        }

    def _generate_empty_report(self) -> Dict:
        report = {
            "timestamp": str(__import__("datetime").datetime.now().isoformat()),
            "total_functions": 0,
            "covered_functions": 0,
            "functions_with_2_mutations": 0,
            "coverage_percent": 0,
            "total_mutations": 0,
            "killed_mutations": 0,
            "mutation_score": 0,
            "threshold_required": self.mutation_threshold,
            "coverage_threshold": self.coverage_threshold,
            "mutation_score_threshold": self.mutation_score_threshold,
            "threshold_passed": False,
            "functions": {},
            "mutations": [],
        }
        self._save_report(report)
        return report

    def _save_report(self, report: Dict):
        report_dir = self.project_root / "reports" / "mutation"
        report_dir.mkdir(parents=True, exist_ok=True)

        report_path = report_dir / "mutation_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\nОтчет сохранен: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="Mutation Test Runner")
    parser.add_argument("--project-root", type=Path, default=Path("."), help="Корневая директория проекта")
    parser.add_argument("--generate-report", action="store_true", help="Сгенерировать отчет о мутациях")
    parser.add_argument(
        "--language", type=str, choices=["python", "nodejs", "rust", "go", "csharp"], help="Язык для анализа"
    )

    args = parser.parse_args()

    runner = MutationRunner(args.project_root)

    if args.generate_report:
        languages = [args.language] if args.language else None
        report = runner.run_all_mutations(languages)
        if not report.get("threshold_passed", False):
            sys.exit(1)
    else:
        languages = [args.language] if args.language else ["python", "nodejs", "rust", "go", "csharp"]

        for lang in languages:
            funcs = runner.discover_functions(lang)
            print(f"\n{lang.upper()}: {len(funcs)} функций")
            for func in funcs[:5]:
                print(f"  - {func.name} ({func.file_path}:{func.line_start})")
            if len(funcs) > 5:
                print(f"  ... и ещё {len(funcs) - 5}")


if __name__ == "__main__":
    main()
