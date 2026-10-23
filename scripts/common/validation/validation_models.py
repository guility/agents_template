"""Shared result types for post-agent validation checks."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class ValidationStage(Enum):
    TRACEABILITY = "traceability"
    SECURITY = "security"
    FORMATTING = "formatting"
    COMPLEXITY = "complexity"
    TEST_COVERAGE = "test_coverage"
    MUTATION_COVERAGE = "mutation_coverage"


@dataclass
class ValidationResult:
    stage: ValidationStage
    passed: bool
    message: str
    details: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
