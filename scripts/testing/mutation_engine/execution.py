import shlex
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

from .models import MutationResult


class MutationExecution:
    def _test_command(self, language: str) -> List[str]:
        configured = self.config.get("test_commands", {}).get(language)
        if configured:
            return shlex.split(configured) if isinstance(configured, str) else list(configured)
        defaults = {
            "python": [sys.executable, "-m", "pytest"],
            "nodejs": ["pnpm", "test", "--", "--runInBand"],
            "rust": ["cargo", "test", "--all-features"],
            "go": ["go", "test", "./..."],
            "csharp": ["dotnet", "test"],
        }
        return defaults[language]

    def _project_directory(self, language: str) -> Path:
        configured = self.config.get("project_directories", {}).get(language)
        return self.project_root / (configured or f"src/templates/{language}")

    def _execute_tests(self, language: str):
        command = self._test_command(language)
        try:
            result = subprocess.run(
                command,
                cwd=self._project_directory(language),
                capture_output=True,
                text=True,
                timeout=int(self.config.get("test_timeout_seconds", 120)),
            )
            return result.returncode, result.stdout + result.stderr, None
        except (OSError, subprocess.TimeoutExpired) as error:
            return None, "", str(error)

    def _baseline_error(self, language: str) -> Optional[str]:
        if language not in self._baseline_errors:
            return_code, output, error = self._execute_tests(language)
            if error or return_code != 0:
                details = error or output[-1000:]
                self._baseline_errors[language] = f"Baseline tests failed: {details}"
            else:
                self._baseline_errors[language] = None
        return self._baseline_errors[language]

    def run_mutation_tests(self, mutation: MutationResult) -> bool:
        """Apply one mutation, execute tests, and restore the original source."""
        if not mutation.created or not mutation.mutated_source:
            return False
        baseline_error = self._baseline_error(mutation.language)
        if baseline_error:
            mutation.error_message = baseline_error
            return False

        file_path = Path(mutation.file_path)
        if file_path.read_text(encoding="utf-8") != mutation.original_source:
            mutation.error_message = "Source changed after mutation generation"
            return False

        try:
            file_path.write_text(mutation.mutated_source, encoding="utf-8")
            return_code, output, error = self._execute_tests(mutation.language)
            if error:
                mutation.error_message = error
                return False
            mutation.test_that_killed = " ".join(self._test_command(mutation.language)) if return_code else None
            if return_code == 0:
                mutation.error_message = f"Mutation survived. Test output: {output[-500:]}"
            return return_code != 0
        finally:
            file_path.write_text(mutation.original_source or "", encoding="utf-8")

