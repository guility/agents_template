#!/usr/bin/env python3
"""
Complexity Analyzer - Enforces cyclomatic complexity limits using lizard.
Blocks code with CNC > 10 and identifies God Classes.
"""

import subprocess
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
import xml.etree.ElementTree as ET


class ComplexityAnalyzer:
    """Analyzes code complexity and enforces limits."""
    
    def __init__(self, project_root: str, max_complexity: int = 10):
        self.project_root = Path(project_root)
        self.max_complexity = max_complexity
        self.results = {
            'total_files': 0,
            'total_functions': 0,
            'violations': [],
            'god_classes': [],
            'summary': {}
        }
    
    def run_lizard(self, target_path: str) -> Dict[str, Any]:
        """Run lizard analysis on target path."""
        try:
            result = subprocess.run(
                ['lizard', target_path, '--xml'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0 and not result.stdout:
                return {'error': result.stderr}
            
            # Parse XML output
            root = ET.fromstring(result.stdout)
            return self._parse_lizard_xml(root)
            
        except FileNotFoundError:
            return {'error': 'lizard not found. Install with: pip install lizard'}
        except Exception as e:
            return {'error': str(e)}
    
    def _parse_lizard_xml(self, root: ET.Element) -> Dict[str, Any]:
        """Parse lizard XML output."""
        functions = []
        classes = []
        
        for file_elem in root.findall('.//file'):
            filename = file_elem.get('name', '')
            
            for function in file_elem.findall('.//function'):
                func_data = {
                    'file': filename,
                    'name': function.get('name', ''),
                    'line_start': int(function.get('start_line', 0)),
                    'line_end': int(function.get('end_line', 0)),
                    'complexity': int(function.get('cyclomatic_complexity', 1)),
                    'nloc': int(function.get('nloc', 0)),
                    'tokens': int(function.get('token_count', 0)),
                    'parameters': len(function.findall('param'))
                }
                functions.append(func_data)
            
            # Detect potential God Classes (high NLOC + high complexity)
            for class_elem in file_elem.findall('.//class'):
                class_data = {
                    'file': filename,
                    'name': class_elem.get('name', ''),
                    'line_start': int(class_elem.get('start_line', 0)),
                    'line_end': int(class_elem.get('end_line', 0)),
                    'complexity': int(class_elem.get('cyclomatic_complexity', 1)),
                    'nloc': int(class_elem.get('nloc', 0))
                }
                classes.append(class_data)
        
        return {'functions': functions, 'classes': classes}
    
    def analyze(self, patterns: List[str] = None) -> Dict[str, Any]:
        """Analyze entire project for complexity violations."""
        if patterns is None:
            patterns = ['*.py', '*.js', '*.ts', '*.rs', '*.go', '*.cs', '*.cpp', '*.c', '*.h']
        
        all_functions = []
        all_classes = []
        
        for pattern in patterns:
            for file_path in self.project_root.rglob(pattern):
                # Skip test files, vendor, node_modules, etc.
                if any(skip in str(file_path) for skip in ['test', 'node_modules', 'vendor', '.git', '__pycache__']):
                    continue
                
                result = self.run_lizard(str(file_path))
                
                if 'functions' in result:
                    all_functions.extend(result['functions'])
                if 'classes' in result:
                    all_classes.extend(result['classes'])
        
        self.results['total_files'] = len(set(f['file'] for f in all_functions))
        self.results['total_functions'] = len(all_functions)
        
        # Find violations (complexity > max_complexity)
        self.results['violations'] = [
            func for func in all_functions 
            if func['complexity'] > self.max_complexity
        ]
        
        # Find God Classes (NLOC > 500 OR complexity > 20)
        self.results['god_classes'] = [
            cls for cls in all_classes
            if cls['nloc'] > 500 or cls['complexity'] > 20
        ]
        
        # Generate summary
        self.results['summary'] = {
            'max_allowed_complexity': self.max_complexity,
            'functions_analyzed': len(all_functions),
            'violations_count': len(self.results['violations']),
            'god_classes_count': len(self.results['god_classes']),
            'average_complexity': sum(f['complexity'] for f in all_functions) / len(all_functions) if all_functions else 0,
            'max_complexity_found': max((f['complexity'] for f in all_functions), default=0)
        }
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate human-readable complexity report."""
        summary = self.results['summary']
        
        report = f"""
=== CODE COMPLEXITY REPORT ===
Files Analyzed: {self.results['total_files']}
Functions Analyzed: {self.results['total_functions']}
Maximum Allowed Complexity: {self.max_complexity}
Average Complexity: {summary['average_complexity']:.2f}
Maximum Complexity Found: {summary['max_complexity_found']}

VIOLATIONS SUMMARY:
- Functions exceeding complexity limit: {summary['violations_count']}
- God Classes detected: {summary['god_classes_count']}

COMPLIANCE CHECK:
- All functions ≤ {self.max_complexity}: {'✓' if summary['violations_count'] == 0 else '✗'}
- No God Classes: {'✓' if summary['god_classes_count'] == 0 else '✗'}
"""
        
        if self.results['violations']:
            report += "\n=== COMPLEXITY VIOLATIONS ===\n"
            for violation in sorted(self.results['violations'], key=lambda x: x['complexity'], reverse=True)[:20]:
                report += f"  {violation['file']}:{violation['line_start']} "
                report += f"{violation['name']} (CNC={violation['complexity']}, NLOC={violation['nloc']})\n"
        
        if self.results['god_classes']:
            report += "\n=== GOD CLASSES DETECTED ===\n"
            for god_class in self.results['god_classes'][:10]:
                report += f"  {god_class['file']}:{god_class['line_start']} "
                report += f"{god_class['name']} (CNC={god_class['complexity']}, NLOC={god_class['nloc']})\n"
        
        return report
    
    def check_compliance(self) -> bool:
        """Check if code meets complexity requirements."""
        return len(self.results['violations']) == 0 and len(self.results['god_classes']) == 0


def main():
    parser = argparse.ArgumentParser(description='Code Complexity Analyzer')
    parser.add_argument('--root', default='.', help='Project root directory')
    parser.add_argument('--max-complexity', type=int, default=10, 
                        help='Maximum allowed cyclomatic complexity (default: 10)')
    parser.add_argument('--output', default='complexity_report.json', help='Output JSON report file')
    parser.add_argument('--patterns', nargs='+', default=None,
                        help='File patterns to analyze (e.g., *.py *.js)')
    
    args = parser.parse_args()
    
    analyzer = ComplexityAnalyzer(args.root, args.max_complexity)
    results = analyzer.analyze(args.patterns)
    report = analyzer.generate_report()
    
    print(report)
    
    # Save JSON report
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed report saved to: {args.output}")
    
    # Exit with error if violations found
    if not analyzer.check_compliance():
        print(f"\n❌ FAILED: {len(results['violations'])} complexity violations found!")
        print("Refactor functions to reduce cyclomatic complexity below", args.max_complexity)
        sys.exit(1)
    else:
        print("\n✅ PASSED: All functions meet complexity requirements!")
        sys.exit(0)


if __name__ == '__main__':
    main()
