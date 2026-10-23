import json
from pathlib import Path
from typing import Dict, List

from .language_discovery import LanguageFunctionDiscovery
from .models import FunctionInfo


class MutationDiscovery(LanguageFunctionDiscovery):
    def _load_config(self) -> Dict:
        """Загрузка конфигурации."""
        config_path = self.project_root / ".mutation_config.json"
        if config_path.exists():
            with open(config_path, "r") as f:
                return json.load(f)
        return {}

    def discover_functions(self, language: str = "python") -> List[FunctionInfo]:
        """Обнаружение функций в коде."""
        functions = []

        if language == "python":
            functions = self._discover_python_functions()
        elif language in ("javascript", "nodejs"):
            functions = self._discover_js_functions()
        elif language == "rust":
            functions = self._discover_rust_functions()
        elif language == "go":
            functions = self._discover_go_functions()
        elif language == "csharp":
            functions = self._discover_csharp_functions()

        return functions

    def _discover_python_functions(self) -> List[FunctionInfo]:
        """Обнаружение функций Python."""
        functions = []
        src_dir = self._project_directory("python") / "src"

        if not src_dir.exists():
            return functions

        for py_file in src_dir.rglob("*.py"):
            if "test" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                current_func = None

                for i, line in enumerate(lines):
                    stripped = line.lstrip()

                    if stripped.startswith("def "):
                        func_name = stripped[4:].split("(")[0]

                        if current_func:
                            current_func.line_end = i

                        current_func = FunctionInfo(
                            name=func_name, file_path=str(py_file), line_start=i + 1, line_end=i + 1, language="python"
                        )
                        functions.append(current_func)

                if current_func and lines:
                    current_func.line_end = len(lines)

            except Exception as e:
                print(f"[WARN] Ошибка парсинга {py_file}: {e}")

        return functions

