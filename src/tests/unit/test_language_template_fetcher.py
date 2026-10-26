import subprocess
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
LANGUAGE_TAGS = {
    "python": "python/v2.0.0",
    "nodejs": "nodejs/v1.0.1",
    "rust": "rust/v1.0.1",
    "go": "go/v1.0.1",
    "csharp": "csharp/v1.0.2",
    "cpp": "cpp/v1.0.0",
    "cuda": "cuda/v1.0.0",
}


class LanguageTemplateFetcherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        repository = self._create_tagged_repository()
        self.fetcher = self._install_fetcher(repository)

    def _git(self, repository: Path, *arguments: str) -> None:
        command = ["git", "-C", str(repository), *arguments]
        subprocess.run(command, check=True, capture_output=True)

    def _create_tagged_repository(self) -> Path:
        repository = self.root / "language-source"
        (repository / "template").mkdir(parents=True)
        self._git(self.root, "init", "-q", str(repository))
        self._git(repository, "config", "user.name", "Fetcher test")
        self._git(
            repository, "config", "user.email", "fetcher-test@example.invalid"
        )
        marker = repository / "template/marker.txt"
        for language, tag in LANGUAGE_TAGS.items():
            marker.write_text(language, encoding="utf-8")
            self._git(repository, "add", "template/marker.txt")
            self._git(repository, "commit", "-qm", language)
            self._git(repository, "tag", tag)
        bare = self.root / "language-source.git"
        subprocess.run(
            ["git", "clone", "-q", "--bare", str(repository), str(bare)],
            check=True,
        )
        return bare

    def _install_fetcher(self, repository: Path) -> Path:
        script_path = (
            REPOSITORY_ROOT / "scripts/setup/fetch_language_templates.sh"
        )
        script = script_path.read_text(encoding="utf-8")
        remote = "https://github.com/guility/agents-template-langs.git"
        self.assertEqual(1, script.count(remote))
        project_script = (
            self.root / "project/scripts/setup/fetch_language_templates.sh"
        )
        project_script.parent.mkdir(parents=True)
        project_script.write_text(
            script.replace(remote, str(repository)), encoding="utf-8"
        )
        return project_script

    def _fetch(self, language: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(self.fetcher), language],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_explicit_cpp_and_cuda_fetch_their_immutable_tags(self) -> None:
        cache = self.root / "project/src/templates"
        for language in ("cpp", "cuda"):
            result = self._fetch(language)
            self.assertEqual(0, result.returncode, result.stderr)
            marker = cache / language / "marker.txt"
            self.assertEqual(language, marker.read_text(encoding="utf-8"))

    def test_all_fetches_published_set_without_proposed_languages(
        self,
    ) -> None:
        result = self._fetch("all")
        self.assertEqual(0, result.returncode, result.stderr)
        cache = self.root / "project/src/templates"
        for language in ("python", "nodejs", "rust", "go", "csharp"):
            marker = cache / language / "marker.txt"
            self.assertEqual(language, marker.read_text(encoding="utf-8"))
        self.assertFalse((cache / "cpp").exists())
        self.assertFalse((cache / "cuda").exists())

    def test_unknown_language_fails_without_creating_cache(self) -> None:
        result = self._fetch("unknown")
        self.assertEqual(2, result.returncode)
        self.assertFalse((self.root / "project/src/templates").exists())
