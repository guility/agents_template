import subprocess
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
REMOTE = "https://github.com/guility/agents-template-langs.git"
TAGS = {
    "python": "python/v2.0.0",
    "nodejs": "nodejs/v1.0.1",
    "rust": "rust/v1.0.1",
    "go": "go/v1.0.1",
    "csharp": "csharp/v1.0.2",
    "lean": "lean/v1.0.0",
}


class LeanTemplateFetcherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.fetcher = self._prepare_repositories()

    def _git(self, repository: Path, *arguments: str) -> None:
        subprocess.run(
            ["git", "-C", str(repository), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )

    def _prepare_repositories(self) -> Path:
        source = self.root / "source"
        (source / "template").mkdir(parents=True)
        self._git(self.root, "init", "-q", str(source))
        self._git(source, "config", "user.name", "Fetcher test")
        self._git(source, "config", "user.email", "fetcher@example.invalid")
        marker = source / "template/marker.txt"
        for language, tag in TAGS.items():
            marker.write_text(language, encoding="utf-8")
            self._git(source, "add", "template/marker.txt")
            self._git(source, "commit", "-qm", language)
            self._git(source, "tag", tag)
        bare = self.root / "source.git"
        subprocess.run(["git", "clone", "-q", "--bare", str(source), str(bare)], check=True)
        script = REPOSITORY_ROOT / "scripts/setup/fetch_language_templates.sh"
        project_script = self.root / "project/scripts/setup/fetch_language_templates.sh"
        project_script.parent.mkdir(parents=True)
        content = script.read_text(encoding="utf-8")
        if content.count(REMOTE) != 1:
            raise AssertionError("fetcher remote should occur exactly once")
        project_script.write_text(content.replace(REMOTE, str(bare)), encoding="utf-8")
        return project_script

    def _fetch(self, language: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(self.fetcher), language],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_explicit_lean_tag_copies_the_component_template(self) -> None:
        result = self._fetch("lean")
        self.assertEqual(0, result.returncode, result.stderr)
        marker = self.root / "project/src/templates/lean/marker.txt"
        self.assertEqual("lean", marker.read_text(encoding="utf-8"))

    def test_all_fetches_each_published_language_tag(self) -> None:
        result = self._fetch("all")
        self.assertEqual(0, result.returncode, result.stderr)
        cache = self.root / "project/src/templates"
        for language in TAGS:
            marker = cache / language / "marker.txt"
            self.assertEqual(language, marker.read_text(encoding="utf-8"))

    def test_unknown_language_fails_before_creating_template_cache(self) -> None:
        result = self._fetch("unknown")
        self.assertEqual(2, result.returncode)
        self.assertFalse((self.root / "project/src/templates").exists())
