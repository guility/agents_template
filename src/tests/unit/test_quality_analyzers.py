import importlib.util
import sys
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, REPOSITORY_ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


import tempfile
import xml.etree.ElementTree as element_tree

complexity_module = load_module("complexity_analyzer", "scripts/testing/complexity_analyzer.py")
traceability_module = load_module("traceability_matrix", "scripts/testing/traceability_matrix.py")


class ComplexityAnalyzerTests(unittest.TestCase):
    """Ensure analysis tool failures make the gate fail closed."""

    def test_lizard_error_fails_compliance(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "sample.py"
            source.write_text("def sample():\n    return 1\n", encoding="utf-8")
            analyzer = complexity_module.ComplexityAnalyzer(directory)
            analyzer.run_lizard = lambda _: {"error": "lizard failed"}

            results = analyzer.analyze(["*.py"])

        self.assertEqual(1, len(results["analysis_errors"]))
        self.assertFalse(analyzer.check_compliance())

    def test_actual_lizard_xml_schema_is_parsed(self):
        xml = """
        <cppncss><measure type="Function">
          <item name="sample(...) at src/sample.py:7">
            <value>1</value><value>4</value><value>3</value>
          </item>
        </measure></cppncss>
        """
        analyzer = complexity_module.ComplexityAnalyzer(".")

        result = analyzer._parse_lizard_xml(element_tree.fromstring(xml))

        self.assertEqual("sample", result["functions"][0]["name"])
        self.assertEqual(3, result["functions"][0]["complexity"])

    def test_testing_directory_is_not_mistaken_for_tests(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "testing" / "sample.py"
            source.parent.mkdir()
            source.write_text("def sample():\n    return 1\n", encoding="utf-8")
            analyzer = complexity_module.ComplexityAnalyzer(directory)
            analyzer.run_lizard = lambda _: {"functions": [], "classes": []}

            results = analyzer.analyze(["*.py"])

        self.assertEqual(1, results["total_files"])


class TraceabilityMatrixTests(unittest.TestCase):
    """Ensure tests and cached language templates are not implementation modules."""

    def test_code_modules_only_include_production_core(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            production = root / "src/core/application"
            test_files = root / "src/tests"
            cached_template = root / "src/templates/python/src"
            production.mkdir(parents=True)
            test_files.mkdir(parents=True)
            cached_template.mkdir(parents=True)
            (production / "service.py").write_text("def serve():\n    return True\n", encoding="utf-8")
            (test_files / "test_service.py").write_text("def test_serve():\n    pass\n", encoding="utf-8")
            (cached_template / "template.py").write_text("def template():\n    return True\n", encoding="utf-8")

            modules = traceability_module.TraceabilityMatrix(directory).parse_code_modules()

        self.assertEqual(1, len(modules))
        self.assertTrue(all("/src/core/" in path.replace("\\", "/") for path in modules))
