import re
from typing import Optional

from .models import FunctionInfo, MutationResult, MutationType


class MutationStrategies:
    def _mutate_return_value(self, func: FunctionInfo) -> Optional[MutationResult]:
        pattern = r"^(?P<indent>[ \t]*)return[ \t]+(?P<expr>[^\n#]+)(?P<comment>[ \t]*(?:#.*)?)$"

        def negate_return(match):
            expression = match.group("expr").strip()
            return f'{match.group("indent")}return not ({expression}){match.group("comment")}'

        return self._build_mutation(func, MutationType.RETURN_VALUE, "return", pattern, negate_return)

    def _mutate_conditional(self, func: FunctionInfo) -> Optional[MutationResult]:
        operators = {"==": "!=", "!=": "==", ">=": "<", "<=": ">", ">": "<=", "<": ">="}
        pattern = r"(?P<left>[\w.)\]]+)\s*(?P<op>==|!=|>=|<=|>|<)\s*(?P<right>[\w.(\[\]-]+)"

        def replace_operator(match):
            return f'{match.group("left")} {operators[match.group("op")]} {match.group("right")}'

        return self._build_mutation(func, MutationType.CONDITIONAL_NEGATION, "conditional", pattern, replace_operator)

    def _mutate_arithmetic(self, func: FunctionInfo) -> Optional[MutationResult]:
        operators = {"+": "-", "-": "+", "*": "/", "/": "*"}
        pattern = r"(?P<left>[\w.)\]]+)\s+(?P<op>[+*/-])\s+(?P<right>[\w.(\[\]-]+)"

        def replace_operator(match):
            return f'{match.group("left")} {operators[match.group("op")]} {match.group("right")}'

        return self._build_mutation(func, MutationType.ARITHMETIC_OPERATOR, "arithmetic", pattern, replace_operator)

    def _mutate_boolean(self, func: FunctionInfo) -> Optional[MutationResult]:
        values = {"True": "False", "False": "True", "true": "false", "false": "true"}
        return self._build_mutation(
            func,
            MutationType.BOOLEAN_LITERAL,
            "boolean",
            r"\b(True|False|true|false)\b",
            lambda match: values[match.group(0)],
        )

