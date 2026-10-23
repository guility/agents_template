from typing import List

from .models import FunctionInfo


class LanguageFunctionDiscovery:
    def _discover_js_functions(self) -> List[FunctionInfo]:
        return self._generic_function_discovery("nodejs", ["js", "ts"])

    def _discover_rust_functions(self) -> List[FunctionInfo]:
        return self._generic_function_discovery("rust", ["rs"])

    def _discover_go_functions(self) -> List[FunctionInfo]:
        return self._generic_function_discovery("go", ["go"])

    def _discover_csharp_functions(self) -> List[FunctionInfo]:
        return self._generic_function_discovery("csharp", ["cs"])

    def _generic_function_discovery(self, language: str, extensions: List[str]) -> List[FunctionInfo]:
        """Универсальное обнаружение функций."""
        functions = []
        src_dir = self._project_directory(language) / "src"

        if not src_dir.exists():
            return functions

        for ext in extensions:
            for code_file in src_dir.rglob(f"*.{ext}"):
                if "test" in str(code_file):
                    continue

                try:
                    with open(code_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if any(kw in line for kw in ["fn ", "function ", "func ", "public ", "private "]):
                            func_name = f"func_{language}_{i}"
                            functions.append(
                                FunctionInfo(
                                    name=func_name,
                                    file_path=str(code_file),
                                    line_start=i + 1,
                                    line_end=min(i + 20, len(lines)),
                                    language=language,
                                )
                            )
                except Exception as e:
                    print(f"[WARN] Ошибка парсинга {code_file}: {e}")

        return functions

