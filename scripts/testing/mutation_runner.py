#!/usr/bin/env python3
"""Mutation test runner command line entry point."""

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from mutation_engine.discovery import MutationDiscovery
from mutation_engine.execution import MutationExecution
from mutation_engine.generation import MutationGeneration
from mutation_engine.models import FunctionInfo, MutationResult, MutationType
from mutation_engine.reporting import MutationReporting


class MutationRunner(
    MutationDiscovery,
    MutationGeneration,
    MutationExecution,
    MutationReporting,
):
    """Compose the mutation runner implementation modules."""

    def __init__(self, project_root: Path, config=None):
        self.project_root = Path(project_root)
        self.config = config or self._load_config()
        self.results = []
        self.functions = {}
        self._baseline_errors = {}
        self.mutation_threshold = 2
        self.coverage_threshold = 100.0
        self.mutation_score_threshold = 100.0


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
