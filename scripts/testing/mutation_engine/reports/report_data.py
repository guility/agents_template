import json
from pathlib import Path
from typing import Dict

from ..models import FunctionInfo, MutationResult


class MutationReportData:
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


