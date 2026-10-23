"""Text parsers used by the traceability matrix."""

import re
from typing import List, Set


class TraceabilityParsers:
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
        # Match patterns like REQ-001, [REQ-002], @requirement REQ-003
        patterns = [
            r'REQ-\d+',
            r'\[REQ-(\d+)\]',
            r'@requirement\s+REQ-\d+'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    refs.add(f'REQ-{match[0]}')
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
