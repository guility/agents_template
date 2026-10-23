import re
from pathlib import Path
from typing import List, Optional

from .models import FunctionInfo, MutationResult, MutationType
from .strategies import MutationStrategies


class MutationGeneration(MutationStrategies):
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

