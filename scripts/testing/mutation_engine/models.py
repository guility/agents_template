from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MutationType(Enum):
    """Типы мутаций."""

    RETURN_VALUE = "return_value"
    CONDITIONAL_NEGATION = "conditional_negation"
    ARITHMETIC_OPERATOR = "arithmetic_operator"
    BOOLEAN_LITERAL = "boolean_literal"
    EXCEPTION_SUPPRESSION = "exception_suppression"
    LOOP_BOUNDARY = "loop_boundary"


@dataclass
class FunctionInfo:
    """Информация о функции."""

    name: str
    file_path: str
    line_start: int
    line_end: int
    language: str
    mutations_generated: int = 0
    mutations_killed: int = 0


@dataclass
class MutationResult:
    """Результат мутационного теста."""

    function_name: str
    mutation_type: MutationType
    mutation_id: str
    created: bool
    killed: bool
    language: str = ""
    file_path: str = ""
    original_source: Optional[str] = None
    mutated_source: Optional[str] = None
    test_that_killed: Optional[str] = None
    error_message: Optional[str] = None


