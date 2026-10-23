#!/usr/bin/env python3
"""
Traceability Matrix Generator - Links requirements to tests and code.
Ensures full coverage of requirements by tests and implementation.
"""

import os
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Set, Any

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from traceability_parsers import TraceabilityParsers


class TraceabilityMatrix(TraceabilityParsers):
    """Generates and validates traceability between requirements, tests, and code."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.requirements_dir = self.project_root / 'docs' / 'requirements'
        self.tests_dir = self.project_root / 'src' / 'tests'
        self.src_dir = self.project_root / 'src'

        self.matrix = {
            'requirements': {},
            'tests': {},
            'code_modules': {},
            'links': {
                'req_to_tests': {},
                'req_to_code': {},
                'tests_to_req': {},
                'code_to_req': {}
            },
            'gaps': {
                'untested_requirements': [],
                'unimplemented_requirements': [],
                'orphan_tests': [],
                'orphan_code': []
            }
        }

    def parse_requirements(self) -> Dict[str, Any]:
        """Parse all requirement files."""
        requirements = {}

        if not self.requirements_dir.exists():
            return requirements

        for req_file in self.requirements_dir.glob('REQ-*.md'):
            req_id = req_file.stem  # e.g., REQ-001

            with open(req_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract metadata from frontmatter
            req_data = {
                'id': req_id,
                'file': str(req_file),
                'title': self._extract_title(content),
                'status': self._extract_status(content),
                'related_to': self._extract_related(content),
                'acceptance_criteria': self._extract_acceptance_criteria(content)
            }

            requirements[req_id] = req_data

        self.matrix['requirements'] = requirements
        return requirements

    def parse_tests(self) -> Dict[str, Any]:
        """Parse test files and extract requirement references."""
        tests = {}

        if not self.tests_dir.exists():
            return tests

        for test_file in self.tests_dir.rglob('*test*.py'):
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find requirement references in comments/docstrings
            req_refs = self._find_requirement_refs(content)

            tests[str(test_file)] = {
                'file': str(test_file),
                'functions': self._extract_test_functions(content),
                'requirements_referenced': list(req_refs)
            }

        self.matrix['tests'] = tests
        return tests

    def parse_code_modules(self) -> Dict[str, Any]:
        """Parse source code modules and extract requirement references."""
        modules = {}

        if not self.src_dir.exists():
            return modules

        for src_file in self.src_dir.rglob('*.py'):
            with open(src_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find requirement references in docstrings/comments
            req_refs = self._find_requirement_refs(content)

            modules[str(src_file)] = {
                'file': str(src_file),
                'classes': self._extract_classes(content),
                'functions': self._extract_functions(content),
                'requirements_referenced': list(req_refs)
            }

        self.matrix['code_modules'] = modules
        return modules

    def build_links(self):
        """Build traceability links between requirements, tests, and code."""
        # Link requirements to tests
        for req_id in self.matrix['requirements']:
            linked_tests = []
            for test_file, test_data in self.matrix['tests'].items():
                if req_id in test_data['requirements_referenced']:
                    linked_tests.append(test_file)
            self.matrix['links']['req_to_tests'][req_id] = linked_tests

        # Link requirements to code
        for req_id in self.matrix['requirements']:
            linked_code = []
            for mod_file, mod_data in self.matrix['code_modules'].items():
                if req_id in mod_data['requirements_referenced']:
                    linked_code.append(mod_file)
            self.matrix['links']['req_to_code'][req_id] = linked_code

        # Reverse links: tests to requirements
        for test_file, test_data in self.matrix['tests'].items():
            self.matrix['links']['tests_to_req'][test_file] = test_data['requirements_referenced']

        # Reverse links: code to requirements
        for mod_file, mod_data in self.matrix['code_modules'].items():
            self.matrix['links']['code_to_req'][mod_file] = mod_data['requirements_referenced']

    def _record_unlinked_requirements(self, link_name: str, gap_name: str) -> None:
        links = self.matrix['links'][link_name]
        gaps = self.matrix['gaps'][gap_name]
        gaps.extend(req_id for req_id in self.matrix['requirements'] if not links.get(req_id))

    def _record_orphans(self, source_name: str, gap_name: str, skip_infrastructure: bool = False) -> None:
        for path, item in self.matrix[source_name].items():
            if item['requirements_referenced']:
                continue
            if skip_infrastructure and ('infrastructure' in path or 'utils' in path):
                continue
            self.matrix['gaps'][gap_name].append(path)

    def identify_gaps(self):
        """Identify gaps in traceability."""
        self._record_unlinked_requirements('req_to_tests', 'untested_requirements')
        self._record_unlinked_requirements('req_to_code', 'unimplemented_requirements')
        self._record_orphans('tests', 'orphan_tests')
        self._record_orphans('code_modules', 'orphan_code', skip_infrastructure=True)

    def _render_coverage(self) -> str:
        total = len(self.matrix['requirements'])
        tested = total - len(self.matrix['gaps']['untested_requirements'])
        implemented = total - len(self.matrix['gaps']['unimplemented_requirements'])
        tested_pct = tested / total * 100 if total else 0
        implemented_pct = implemented / total * 100 if total else 0
        return (
            "\nREQUIREMENTS COVERAGE:\n"
            f"Total Requirements: {total}\n"
            f"Tested: {tested}/{total} ({tested_pct:.1f}%)\n"
            f"Implemented: {implemented}/{total} ({implemented_pct:.1f}%)\n"
        )

    def _render_gap(self, key: str, title: str, limit: int, symbol: str, detail: str = '') -> str:
        entries = self.matrix['gaps'][key]
        if not entries:
            return ''
        lines = [f"\n{symbol} {title} ({len(entries)}){detail or ':'}\n"]
        lines.extend(f"   - {Path(item).name}\n" for item in entries[:limit])
        return ''.join(lines)

    def generate_report(self) -> str:
        """Generate traceability matrix report."""
        gaps = [
            self._render_gap('untested_requirements', 'UNTESTED REQUIREMENTS', 10, '❌'),
            self._render_gap('unimplemented_requirements', 'UNIMPLEMENTED REQUIREMENTS', 10, '❌'),
            self._render_gap('orphan_tests', 'ORPHAN TESTS', 5, '⚠️', ': Tests without requirement references'),
            self._render_gap('orphan_code', 'ORPHAN CODE', 5, '⚠️', ': Modules without requirement references'),
        ]
        tested = not self.matrix['gaps']['untested_requirements']
        implemented = not self.matrix['gaps']['unimplemented_requirements']
        compliance = (
            "\n=== COMPLIANCE CHECK ===\n"
            f"All requirements tested: {'✓' if tested else '✗'}\n"
            f"All requirements implemented: {'✓' if implemented else '✗'}\n"
        )
        return "=== TRACEABILITY MATRIX REPORT ===\n" + self._render_coverage() + "\n=== GAPS IDENTIFIED ===\n" + ''.join(gaps) + compliance

    def check_compliance(self) -> bool:
        """Check if traceability requirements are met."""
        return (
            len(self.matrix['gaps']['untested_requirements']) == 0 and
            len(self.matrix['gaps']['unimplemented_requirements']) == 0
        )

    def save_matrix(self, output_file: str):
        """Save traceability matrix to JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.matrix, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description='Traceability Matrix Generator')
    parser.add_argument('--root', default='.', help='Project root directory')
    parser.add_argument('--output', default='traceability_matrix.json',
                        help='Output JSON file')

    args = parser.parse_args()

    matrix = TraceabilityMatrix(args.root)

    print("Parsing requirements...")
    matrix.parse_requirements()

    print("Parsing tests...")
    matrix.parse_tests()

    print("Parsing code modules...")
    matrix.parse_code_modules()

    print("Building traceability links...")
    matrix.build_links()

    print("Identifying gaps...")
    matrix.identify_gaps()

    report = matrix.generate_report()
    print(report)

    matrix.save_matrix(args.output)
    print(f"\nDetailed matrix saved to: {args.output}")

    if not matrix.check_compliance():
        print("\n❌ FAILED: Traceability gaps detected!")
        print("Ensure all requirements have tests and implementation.")
        exit(1)
    else:
        print("\n✅ PASSED: Full traceability achieved!")
        exit(0)


if __name__ == '__main__':
    main()
