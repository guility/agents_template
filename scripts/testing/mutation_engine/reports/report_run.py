from typing import Dict, List, Optional

from ..models import FunctionInfo


class MutationReportRun:
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

