#!/usr/bin/env python3
"""
Complexity Analyzer - Enforces cyclomatic complexity limits using lizard.
Blocks code with CNC > 10 and identifies God Classes.
"""

import argparse
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List


class ComplexityAnalyzer:
    """Analyzes code complexity and enforces limits."""

    def __init__(self, project_root: str, max_complexity: int = 10):
        self.project_root = Path(project_root)
        self.max_complexity = max_complexity
        self.results = {
            "total_files": 0,
            "total_functions": 0,
            "analysis_errors": [],
            "violations": [],
            "god_classes": [],
            "summary": {},
        }

    def run_lizard(self, target_path: str) -> Dict[str, Any]:
        """Run lizard analysis on target path."""
        try:
            result = subprocess.run(["lizard", target_path, "--xml"], capture_output=True, text=True, timeout=60)

            if result.returncode != 0 and not result.stdout:
                return {"error": result.stderr}

            # Parse XML output
            root = ET.fromstring(result.stdout)
            return self._parse_lizard_xml(root)

        except FileNotFoundError:
            return {"error": "lizard not found. Install with: pip install lizard"}
        except Exception as e:
            return {"error": str(e)}

    def _parse_lizard_xml(self, root: ET.Element) -> Dict[str, Any]:
        """Parse lizard XML output."""
        functions = []
        measure = root.find(".//measure[@type='Function']")
        if measure is None:
            raise ValueError("Lizard XML does not contain a Function measure")

        for item in measure.findall("item"):
            values = [value.text for value in item.findall("value")]
            if len(values) < 3:
                raise ValueError("Lizard function item has incomplete metrics")
            name, filename, line = self._parse_function_location(item.get("name", ""))
            functions.append(
                {
                    "file": filename,
                    "name": name,
                    "line_start": line,
                    "line_end": line,
                    "complexity": int(values[2]),
                    "nloc": int(values[1]),
                    "tokens": 0,
                    "parameters": 0,
                }
            )

        return {"functions": functions, "classes": []}

    @staticmethod
    def _parse_function_location(value: str):
        """Split Lizard's '<name>(...) at <path>:<line>' descriptor."""
        match = re.match(r"^(?P<name>.+?)\(\.\.\.\) at (?P<file>.*):(?P<line>\d+)$", value)
        if not match:
            raise ValueError(f"Unexpected Lizard function descriptor: {value}")
        return match.group("name"), match.group("file"), int(match.group("line"))

    def analyze(self, patterns: List[str] = None) -> Dict[str, Any]:
        """Analyze entire project for complexity violations."""
        patterns = patterns or ["*.py", "*.js", "*.ts", "*.rs", "*.go", "*.cs", "*.cpp", "*.c", "*.h"]
        all_functions, all_classes, analyzed_files = self._collect_metrics(self._source_files(patterns))
        self._update_results(all_functions, all_classes, analyzed_files)
        return self.results

    def _source_files(self, patterns: List[str]):
        """Yield selected source files while excluding tests and dependencies."""
        for pattern in patterns:
            for file_path in self.project_root.rglob(pattern):
                if not self._should_skip(file_path):
                    yield file_path

    def _collect_metrics(self, file_paths):
        """Run Lizard for every selected file and retain every tool error."""
        all_functions = []
        all_classes = []
        analyzed_files = set()
        self.results["analysis_errors"] = []
        for file_path in file_paths:
            result = self.run_lizard(str(file_path))
            if "error" in result:
                self.results["analysis_errors"].append(
                    {
                        "file": str(file_path),
                        "error": result["error"] or "unknown lizard error",
                    }
                )
                continue
            analyzed_files.add(str(file_path))
            all_functions.extend(result.get("functions", []))
            all_classes.extend(result.get("classes", []))
        return all_functions, all_classes, analyzed_files

    def _update_results(self, all_functions, all_classes, analyzed_files):
        """Calculate violations and summary values from collected metrics."""
        self.results["total_files"] = len(analyzed_files)
        self.results["total_functions"] = len(all_functions)
        self.results["violations"] = [
            function for function in all_functions if function["complexity"] > self.max_complexity
        ]
        self.results["god_classes"] = [item for item in all_classes if item["nloc"] > 500 or item["complexity"] > 20]
        self.results["summary"] = {
            "max_allowed_complexity": self.max_complexity,
            "functions_analyzed": len(all_functions),
            "analysis_errors_count": len(self.results["analysis_errors"]),
            "violations_count": len(self.results["violations"]),
            "god_classes_count": len(self.results["god_classes"]),
            "average_complexity": (
                sum(f["complexity"] for f in all_functions) / len(all_functions) if all_functions else 0
            ),
            "max_complexity_found": max((f["complexity"] for f in all_functions), default=0),
        }

    @staticmethod
    def _should_skip(file_path: Path) -> bool:
        """Skip test files and dependency directories without substring matches."""
        excluded_directories = {"test", "tests", "node_modules", "vendor", ".git", "__pycache__", ".venv", "venv"}
        if any(part.lower() in excluded_directories for part in file_path.parts):
            return True
        name = file_path.name.lower()
        return name.startswith("test_") or name.endswith(("_test.py", ".test.js", ".test.ts"))

    def generate_report(self) -> str:
        """Generate human-readable complexity report."""
        summary = self.results["summary"]

        report = f"""
=== CODE COMPLEXITY REPORT ===
Files Analyzed: {self.results['total_files']}
Functions Analyzed: {self.results['total_functions']}
Maximum Allowed Complexity: {self.max_complexity}
Average Complexity: {summary['average_complexity']:.2f}
Maximum Complexity Found: {summary['max_complexity_found']}

VIOLATIONS SUMMARY:
- Files that could not be analyzed: {summary['analysis_errors_count']}
- Functions exceeding complexity limit: {summary['violations_count']}
- God Classes detected: {summary['god_classes_count']}

COMPLIANCE CHECK:
- Lizard analyzed every selected file: {'PASS' if summary['analysis_errors_count'] == 0 else 'FAIL'}
- All functions <= {self.max_complexity}: {'PASS' if summary['violations_count'] == 0 else 'FAIL'}
- No God Classes: {'PASS' if summary['god_classes_count'] == 0 else 'FAIL'}
"""

        if self.results["analysis_errors"]:
            report += "\n=== ANALYSIS ERRORS ===\n"
            for error in self.results["analysis_errors"][:20]:
                report += f"  {error['file']}: {error['error']}\n"

        if self.results["violations"]:
            report += "\n=== COMPLEXITY VIOLATIONS ===\n"
            for violation in sorted(self.results["violations"], key=lambda x: x["complexity"], reverse=True)[:20]:
                report += f"  {violation['file']}:{violation['line_start']} "
                report += f"{violation['name']} (CNC={violation['complexity']}, NLOC={violation['nloc']})\n"

        if self.results["god_classes"]:
            report += "\n=== GOD CLASSES DETECTED ===\n"
            for god_class in self.results["god_classes"][:10]:
                report += f"  {god_class['file']}:{god_class['line_start']} "
                report += f"{god_class['name']} (CNC={god_class['complexity']}, NLOC={god_class['nloc']})\n"

        return report

    def check_compliance(self) -> bool:
        """Check if code meets complexity requirements."""
        return (
            not self.results["analysis_errors"] and not self.results["violations"] and not self.results["god_classes"]
        )


def main():
    parser = argparse.ArgumentParser(description="Code Complexity Analyzer")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument(
        "--max-complexity", type=int, default=10, help="Maximum allowed cyclomatic complexity (default: 10)"
    )
    parser.add_argument("--output", default="complexity_report.json", help="Output JSON report file")
    parser.add_argument("--patterns", nargs="+", default=None, help="File patterns to analyze (e.g., *.py *.js)")

    args = parser.parse_args()

    analyzer = ComplexityAnalyzer(args.root, args.max_complexity)
    results = analyzer.analyze(args.patterns)
    report = analyzer.generate_report()

    print(report)

    # Save JSON report
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nDetailed report saved to: {args.output}")

    # Exit with error if violations found
    if not analyzer.check_compliance():
        print(
            f"\nFAILED: {len(results['analysis_errors'])} analysis errors and "
            f"{len(results['violations'])} complexity violations found!"
        )
        sys.exit(1)
    else:
        print("\nPASSED: All functions meet complexity requirements!")
        sys.exit(0)


if __name__ == "__main__":
    main()
