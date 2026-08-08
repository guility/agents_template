"""Regression tests for the actionable PR review findings."""

import importlib.util
import sys
import tempfile
import unittest
import xml.etree.ElementTree as element_tree
from dataclasses import FrozenInstanceError
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, relative_path: str):
    """Load a repository script without requiring package marker files."""
    spec = importlib.util.spec_from_file_location(name, REPOSITORY_ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


mutation_module = load_module("mutation_runner", "scripts/testing/mutation_runner.py")
complexity_module = load_module("complexity_analyzer", "scripts/testing/complexity_analyzer.py")


class MutationRunnerTests(unittest.TestCase):
    """Ensure mutations are applied and judged by real test executions."""

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.project = self.root / "templates" / "python"
        (self.project / "src").mkdir(parents=True)
        (self.project / "tests").mkdir()
        self.source = self.project / "src" / "calculator.py"
        self.source.write_text("def is_positive(value):\n    return value > 0\n", encoding="utf-8")
        test_source = (
            "import sys, unittest\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))\n"
            "from calculator import is_positive\n"
            "class CalculatorTests(unittest.TestCase):\n"
            "    def test_positive_and_negative(self):\n"
            "        self.assertTrue(is_positive(1))\n"
            "        self.assertFalse(is_positive(-1))\n"
        )
        (self.project / "tests" / "test_calculator.py").write_text(test_source, encoding="utf-8")
        config = {
            "test_commands": {"python": [sys.executable, "-m", "unittest", "discover", "-s", "tests"]},
            "test_timeout_seconds": 30,
        }
        self.runner = mutation_module.MutationRunner(self.root, config)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_real_mutations_are_killed_and_source_is_restored(self):
        function = self.runner.discover_functions("python")[0]
        original = self.source.read_text(encoding="utf-8")
        mutations = self.runner.generate_mutations(function)

        self.assertEqual(2, sum(mutation.created for mutation in mutations))
        self.assertTrue(all(self.runner.run_mutation_tests(mutation) for mutation in mutations))
        self.assertEqual(original, self.source.read_text(encoding="utf-8"))

    def test_surviving_mutation_is_not_reported_as_killed(self):
        original = self.source.read_text(encoding="utf-8")
        mutation = mutation_module.MutationResult(
            function_name="is_positive",
            mutation_type=mutation_module.MutationType.CONDITIONAL_NEGATION,
            mutation_id="survivor",
            created=True,
            killed=False,
            language="python",
            file_path=str(self.source),
            original_source=original,
            mutated_source=original.replace("value > 0", "value >= 0"),
        )

        self.assertFalse(self.runner.run_mutation_tests(mutation))
        self.assertEqual(original, self.source.read_text(encoding="utf-8"))

    def test_report_requires_real_mutations_to_be_killed(self):
        report = self.runner.run_all_mutations(["python"])

        self.assertEqual(2, report["total_mutations"])
        self.assertEqual(2, report["killed_mutations"])
        self.assertTrue(report["threshold_passed"])


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


class TemplateAndPathTests(unittest.TestCase):
    """Cover the domain import and reviewed script path contracts."""

    def test_mutable_entity_can_extend_frozen_base(self):
        domain = load_module("template_domain", "templates/python/src/domain/__init__.py")
        entity = domain.Entity(id="entity-1")
        entity.update(status="ignored")

        self.assertIsNotNone(entity.updated_at)
        with self.assertRaises(FrozenInstanceError):
            entity.id = "changed"

    def test_reviewed_helpers_resolve_from_repository(self):
        bootstrap = (REPOSITORY_ROOT / "scripts/setup/bootstrap.sh").read_text(encoding="utf-8")
        test_runner = (REPOSITORY_ROOT / "scripts/common/run-tests.sh").read_text(encoding="utf-8")
        unified = (REPOSITORY_ROOT / "scripts/ci/unified_ci_runner.sh").read_text(encoding="utf-8")
        pre_commit = (REPOSITORY_ROOT / "scripts/hooks/pre-commit.sh").read_text(encoding="utf-8")

        self.assertIn("PROJECT_ROOT=", bootstrap)
        self.assertNotIn("$SCRIPT_DIR/.git", bootstrap)
        self.assertIn("$SCRIPT_DIR/../..", test_runner)
        self.assertIn("$SCRIPTS_DIR/testing/mutation_runner.py", unified)
        self.assertIn("$ROOT_DIR/scripts/common/complexity-check.sh", pre_commit)

    def test_ci_entrypoints_target_nested_templates(self):
        workflow = (REPOSITORY_ROOT / ".github/workflows/ci-cd.yml").read_text(encoding="utf-8")
        gitlab_entrypoint = (REPOSITORY_ROOT / ".gitlab-ci.yml").read_text(encoding="utf-8")

        for language in ("python", "nodejs", "rust", "go", "csharp"):
            self.assertIn(f"working-directory: templates/{language}", workflow)
        self.assertIn("/.gitlab/ci/.gitlab-ci.yml", gitlab_entrypoint)


if __name__ == "__main__":
    unittest.main()
