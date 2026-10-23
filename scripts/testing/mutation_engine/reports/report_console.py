class MutationReportConsole:
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

