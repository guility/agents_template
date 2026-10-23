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


from dataclasses import FrozenInstanceError

class TemplateAndPathTests(unittest.TestCase):
    """Cover the domain import and reviewed script path contracts."""

    def test_mutable_entity_can_extend_frozen_base(self):
        domain = load_module("template_domain", "src/templates/python/src/domain/__init__.py")
        entity = domain.Entity(id="entity-1")
        entity.update(status="ignored")

        self.assertIsNotNone(entity.updated_at)
        with self.assertRaises(FrozenInstanceError):
            entity.id = "changed"

    def test_reviewed_helpers_resolve_from_repository(self):
        bootstrap = (REPOSITORY_ROOT / "scripts/setup/bootstrap.sh").read_text(encoding="utf-8")
        test_runner = (REPOSITORY_ROOT / "scripts/common/run-tests.sh").read_text(encoding="utf-8")
        unified = (REPOSITORY_ROOT / "scripts/ci/unified_ci_runner.sh").read_text(encoding="utf-8")
        unified += (REPOSITORY_ROOT / "scripts/ci/unified/tests.sh").read_text(encoding="utf-8")
        unified += (REPOSITORY_ROOT / "scripts/ci/unified/acceptance.sh").read_text(encoding="utf-8")
        pre_commit = (REPOSITORY_ROOT / "scripts/common/hooks/pre-commit.sh").read_text(encoding="utf-8")

        self.assertIn("PROJECT_ROOT=", bootstrap)
        self.assertNotIn("$SCRIPT_DIR/.git", bootstrap)
        self.assertIn("$SCRIPT_DIR/../..", test_runner)
        self.assertIn("$SCRIPTS_DIR/testing/mutation_runner.py", unified)
        self.assertIn("$ROOT_DIR/scripts/common/complexity-check.sh", pre_commit)

    def test_ci_entrypoints_target_nested_templates(self):
        workflow_dir = REPOSITORY_ROOT / ".github/workflows"
        workflow = (workflow_dir / "ci-cd.yml").read_text(encoding="utf-8")
        gitlab_entrypoint = (REPOSITORY_ROOT / ".gitlab-ci.yml").read_text(encoding="utf-8")

        for language in ("python", "nodejs", "rust", "go", "csharp"):
            template_workflow = (workflow_dir / f"{language}-tests.yml").read_text(encoding="utf-8")
            self.assertIn(f"working-directory: src/templates/{language}", template_workflow)
        self.assertIn("/.gitlab/ci/.gitlab-ci.yml", gitlab_entrypoint)
