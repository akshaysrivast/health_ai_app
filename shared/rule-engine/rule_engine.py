from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Literal


SupportedOperator = Literal[">", "<", "==", ">=", "<="]
SupportedLogic = Literal["AND", "OR"]


@dataclass(frozen=True)
class Condition:
    field: str
    operator: SupportedOperator
    value: Any


@dataclass(frozen=True)
class Rule:
    name: str
    conditions: list[Condition]
    logic: SupportedLogic
    output: dict[str, Any]


class RuleValidationError(ValueError):
    pass


class RuleEngine:
    """
    Secure rule engine using explicit operator evaluation.
    No dynamic code execution or eval-like behavior is used.
    """

    _comparators: dict[str, Callable[[Any, Any], bool]] = {
        ">": lambda left, right: left > right,
        "<": lambda left, right: left < right,
        "==": lambda left, right: left == right,
        ">=": lambda left, right: left >= right,
        "<=": lambda left, right: left <= right,
    }

    def __init__(self, rules: Iterable[dict[str, Any]]) -> None:
        self.rules = [self._validate_and_build_rule(rule) for rule in rules]

    def evaluate(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Evaluate all rules against a context payload and return matched rules.

        Returned entries include the rule identity plus output payload for
        downstream services to consume consistently.
        """
        matched_rules: list[dict[str, Any]] = []

        for rule in self.rules:
            condition_results = [self._evaluate_condition(cond, context) for cond in rule.conditions]
            is_match = all(condition_results) if rule.logic == "AND" else any(condition_results)
            if is_match:
                matched_rules.append(
                    {
                        "name": rule.name,
                        "logic": rule.logic,
                        "output": rule.output,
                    }
                )

        return matched_rules

    def _evaluate_condition(self, condition: Condition, context: dict[str, Any]) -> bool:
        comparator = self._comparators.get(condition.operator)
        if comparator is None:
            raise RuleValidationError(f"Unsupported operator: {condition.operator}")

        left_value = self._get_nested_value(context, condition.field)
        if left_value is None:
            return False

        try:
            return comparator(left_value, condition.value)
        except TypeError:
            # Type mismatch should not crash evaluation.
            return False

    @staticmethod
    def _get_nested_value(payload: dict[str, Any], field_path: str) -> Any:
        """
        Resolve dotted paths (e.g. 'labs.hba1c') in dict-based payloads.
        """
        current: Any = payload
        for part in field_path.split("."):
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
        return current

    def _validate_and_build_rule(self, raw_rule: dict[str, Any]) -> Rule:
        required_keys = {"name", "conditions", "logic", "output"}
        missing = required_keys - set(raw_rule.keys())
        if missing:
            raise RuleValidationError(f"Missing required rule keys: {sorted(missing)}")

        name = raw_rule["name"]
        logic = raw_rule["logic"]
        conditions = raw_rule["conditions"]
        output = raw_rule["output"]

        if not isinstance(name, str) or not name.strip():
            raise RuleValidationError("Rule 'name' must be a non-empty string")

        if logic not in {"AND", "OR"}:
            raise RuleValidationError(f"Rule '{name}' has invalid logic: {logic}")

        if not isinstance(conditions, list) or not conditions:
            raise RuleValidationError(f"Rule '{name}' must define a non-empty 'conditions' list")

        if not isinstance(output, dict):
            raise RuleValidationError(f"Rule '{name}' must define 'output' as an object")

        parsed_conditions: list[Condition] = []
        for cond in conditions:
            if not isinstance(cond, dict):
                raise RuleValidationError(f"Rule '{name}' condition must be an object")
            for key in ("field", "operator", "value"):
                if key not in cond:
                    raise RuleValidationError(f"Rule '{name}' condition missing '{key}'")

            field = cond["field"]
            operator = cond["operator"]
            value = cond["value"]

            if not isinstance(field, str) or not field.strip():
                raise RuleValidationError(f"Rule '{name}' condition field must be non-empty string")
            if operator not in self._comparators:
                raise RuleValidationError(f"Rule '{name}' has unsupported operator: {operator}")

            parsed_conditions.append(Condition(field=field, operator=operator, value=value))

        return Rule(name=name, conditions=parsed_conditions, logic=logic, output=output)
