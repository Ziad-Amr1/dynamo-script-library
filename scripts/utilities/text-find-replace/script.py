"""Bulk text find-and-replace for lists of strings.

This module is designed for Dynamo's CPython 3 engine and for standard Python
tests. It does not import Revit or Dynamo APIs, so the logic can be verified
outside Revit. Use it to clean sheet names, view names, parameter values, or
any other list of strings before writing the result back through Revit nodes.

Inputs:
    values: iterable of strings to process.
    find: non-empty text or regular expression to search for.
    replace: replacement text (empty string deletes matches).
    case_sensitive: match case when True (default).
    whole_value: replace only when the entire string matches (default False).
    use_regex: treat ``find`` and ``replace`` as a regular expression and
        replacement template, including backreferences such as ``\\1``.

Outputs:
    A new list of strings. The input sequence is never modified.
"""

from __future__ import annotations

import re
from typing import Iterable, Sequence


def _validate(values: Iterable[str]) -> list[str]:
    if isinstance(values, str):
        raise TypeError(
            "values must be a list of strings, not a single string. "
            "Wrap a single value in a list."
        )
    result = list(values)
    for index, value in enumerate(result):
        if not isinstance(value, str):
            raise TypeError(
                f"values[{index}] must be a string, got {type(value).__name__}."
            )
    return result


def find_replace(
    values: Iterable[str],
    find: str,
    replace: str = "",
    case_sensitive: bool = True,
    whole_value: bool = False,
    use_regex: bool = False,
) -> list[str]:
    """Return a new list with matches replaced.

    Raises:
        TypeError: if ``values`` is a single string or contains non-strings.
        ValueError: if ``find`` is empty or an invalid regular expression.
    """
    items = _validate(values)
    if not isinstance(find, str) or find == "":
        raise ValueError("find must be a non-empty string.")
    if not isinstance(replace, str):
        raise TypeError("replace must be a string.")

    flags = 0 if case_sensitive else re.IGNORECASE

    if use_regex:
        pattern = f"^(?:{find})$" if whole_value else find
        try:
            compiled = re.compile(pattern, flags)
        except re.error as exc:
            raise ValueError(f"Invalid regular expression: {exc}") from exc
        return [compiled.sub(replace, value) for value in items]

    if whole_value:
        if case_sensitive:
            return [replace if value == find else value for value in items]
        folded = find.casefold()
        return [replace if value.casefold() == folded else value for value in items]

    compiled = re.compile(re.escape(find), flags)
    return [compiled.sub(lambda _match: replace, value) for value in items]


def plan_changes(
    values: Iterable[str],
    find: str,
    replace: str = "",
    case_sensitive: bool = True,
    whole_value: bool = False,
    use_regex: bool = False,
) -> list[dict[str, object]]:
    """Return one record per changed value, useful for previews and logs."""
    items = _validate(values)
    updated = find_replace(
        items,
        find,
        replace,
        case_sensitive=case_sensitive,
        whole_value=whole_value,
        use_regex=use_regex,
    )
    return [
        {"index": index, "before": before, "after": after}
        for index, (before, after) in enumerate(zip(items, updated))
        if before != after
    ]


def _run_from_dynamo() -> list[str]:
    """Adapter used when this file is pasted into a Dynamo Python node.

    Dynamo exposes a list called ``IN``. Optional inputs have defaults so the
    graph can start with only the first three ports connected.
    """
    inputs: Sequence[object] = list(IN)  # type: ignore[name-defined]  # noqa: F821
    if len(inputs) < 2:
        raise ValueError("Connect at least the values and find inputs.")
    return find_replace(
        inputs[0],  # type: ignore[arg-type]
        inputs[1],  # type: ignore[arg-type]
        inputs[2] if len(inputs) > 2 else "",  # type: ignore[arg-type]
        case_sensitive=bool(inputs[3]) if len(inputs) > 3 else True,
        whole_value=bool(inputs[4]) if len(inputs) > 4 else False,
        use_regex=bool(inputs[5]) if len(inputs) > 5 else False,
    )


if "IN" in globals():
    OUT = _run_from_dynamo()
