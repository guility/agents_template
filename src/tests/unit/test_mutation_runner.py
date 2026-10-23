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

mutation_module = load_module("mutation_runner", "scripts/testing/mutation_runner.py")


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
            "project_directories": {"python": "templates/python"},
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
