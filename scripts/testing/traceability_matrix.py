#!/usr/bin/env python3
"""
Traceability Matrix Generator - Links requirements to tests and code.
Ensures full coverage of requirements by tests and implementation.
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Any
import re


class TraceabilityMatrix:
    """Generates and validates traceability between requirements, tests, and code."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.requirements_dir = self.project_root / 'requirements'
        self.tests_dir = self.project_root / 'tests'
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
        
        for req_file in self.requirements_dir.glob('REQ_*.md'):
            req_id = req_file.stem  # e.g., REQ_001
            
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
    
    def identify_gaps(self):
        """Identify gaps in traceability."""
        # Untested requirements
        for req_id, req_data in self.matrix['requirements'].items():
            if not self.matrix['links']['req_to_tests'].get(req_id):
                self.matrix['gaps']['untested_requirements'].append(req_id)
        
        # Unimplemented requirements
        for req_id, req_data in self.matrix['requirements'].items():
            if not self.matrix['links']['req_to_code'].get(req_id):
                self.matrix['gaps']['unimplemented_requirements'].append(req_id)
        
        # Orphan tests (tests without requirement references)
        for test_file, test_data in self.matrix['tests'].items():
            if not test_data['requirements_referenced']:
                self.matrix['gaps']['orphan_tests'].append(test_file)
        
        # Orphan code (code without requirement references)
        for mod_file, mod_data in self.matrix['code_modules'].items():
            if not mod_data['requirements_referenced']:
                # Skip infrastructure/utility code
                if 'infrastructure' not in mod_file and 'utils' not in mod_file:
                    self.matrix['gaps']['orphan_code'].append(mod_file)
    
    def generate_report(self) -> str:
        """Generate traceability matrix report."""
        report = """
=== TRACEABILITY MATRIX REPORT ===

REQUIREMENTS COVERAGE:
"""
        
        total_reqs = len(self.matrix['requirements'])
        tested_reqs = total_reqs - len(self.matrix['gaps']['untested_requirements'])
        implemented_reqs = total_reqs - len(self.matrix['gaps']['unimplemented_requirements'])
        
        report += f"Total Requirements: {total_reqs}\n"
        report += f"Tested: {tested_reqs}/{total_reqs} ({tested_reqs/total_reqs*100:.1f}% if total_reqs > 0 else 0)\n"
        report += f"Implemented: {implemented_reqs}/{total_reqs} ({implemented_reqs/total_reqs*100:.1f}% if total_reqs > 0 else 0)\n"
        
        report += "\n=== GAPS IDENTIFIED ===\n"
        
        if self.matrix['gaps']['untested_requirements']:
            report += f"\n❌ UNTESTED REQUIREMENTS ({len(self.matrix['gaps']['untested_requirements'])}):\n"
            for req_id in self.matrix['gaps']['untested_requirements'][:10]:
                report += f"   - {req_id}\n"
        
        if self.matrix['gaps']['unimplemented_requirements']:
            report += f"\n❌ UNIMPLEMENTED REQUIREMENTS ({len(self.matrix['gaps']['unimplemented_requirements'])}):\n"
            for req_id in self.matrix['gaps']['unimplemented_requirements'][:10]:
                report += f"   - {req_id}\n"
        
        if self.matrix['gaps']['orphan_tests']:
            report += f"\n⚠️  ORPHAN TESTS ({len(self.matrix['gaps']['orphan_tests'])}): Tests without requirement references\n"
            for test_file in self.matrix['gaps']['orphan_tests'][:5]:
                report += f"   - {Path(test_file).name}\n"
        
        if self.matrix['gaps']['orphan_code']:
            report += f"\n⚠️  ORPHAN CODE ({len(self.matrix['gaps']['orphan_code'])}): Modules without requirement references\n"
            for mod_file in self.matrix['gaps']['orphan_code'][:5]:
                report += f"   - {Path(mod_file).name}\n"
        
        # Compliance check
        report += "\n=== COMPLIANCE CHECK ===\n"
        all_tested = len(self.matrix['gaps']['untested_requirements']) == 0
        all_implemented = len(self.matrix['gaps']['unimplemented_requirements']) == 0
        
        report += f"All requirements tested: {'✓' if all_tested else '✗'}\n"
        report += f"All requirements implemented: {'✓' if all_implemented else '✗'}\n"
        
        return report
    
    def check_compliance(self) -> bool:
        """Check if traceability requirements are met."""
        return (
            len(self.matrix['gaps']['untested_requirements']) == 0 and
            len(self.matrix['gaps']['unimplemented_requirements']) == 0
        )
    
    # Helper methods
    def _extract_title(self, content: str) -> str:
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1) if match else 'Unknown'
    
    def _extract_status(self, content: str) -> str:
        match = re.search(r'\*\*Status\*\*:\s*(\w+)', content)
        return match.group(1) if match else 'draft'
    
    def _extract_related(self, content: str) -> List[str]:
        matches = re.findall(r'\*\*Related to\*\*:\s*([\w,\s]+)', content)
        if matches:
            return [r.strip() for r in matches[0].split(',')]
        return []
    
    def _extract_acceptance_criteria(self, content: str) -> List[str]:
        criteria = []
        in_criteria = False
        for line in content.split('\n'):
            if 'Acceptance Criteria' in line:
                in_criteria = True
                continue
            if in_criteria and line.startswith('- [ ]'):
                criteria.append(line[6:].strip())
            elif in_criteria and line.startswith('#'):
                break
        return criteria
    
    def _find_requirement_refs(self, content: str) -> Set[str]:
        refs = set()
        # Match patterns like REQ_001, [REQ_002], @requirement REQ_003
        patterns = [
            r'REQ_\d+',
            r'\[REQ_(\d+)\]',
            r'@requirement\s+REQ_\d+'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    refs.add(f'REQ_{match[0]}')
                else:
                    refs.add(match)
        return refs
    
    def _extract_test_functions(self, content: str) -> List[str]:
        functions = []
        for match in re.finditer(r'def\s+(test_\w+)\s*\(', content):
            functions.append(match.group(1))
        return functions
    
    def _extract_classes(self, content: str) -> List[str]:
        classes = []
        for match in re.finditer(r'class\s+(\w+)', content):
            classes.append(match.group(1))
        return classes
    
    def _extract_functions(self, content: str) -> List[str]:
        functions = []
        for match in re.finditer(r'def\s+(\w+)\s*\(', content):
            functions.append(match.group(1))
        return functions
    
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
