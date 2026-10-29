"""{{name}}.

{{description}}

Target engine: {{python_engine}}.

This starter intentionally has no Revit dependency so its logic can be tested
with standard Python. Replace ``run`` with the real implementation and document
inputs, outputs, assumptions, and limitations in README.md.

The starter avoids syntax that breaks either Dynamo Python 2.7 or CPython 3.
Use type hints only if the tool targets CPython 3 exclusively.

Dynamo note: inside a Dynamo Python node, ``IN`` contains the input list. Keep
Revit-specific handling in a thin wrapper and leave pure logic in testable
functions where practical.
"""


def run(values):
    # type: (list) -> list
    """Return a copy of the input list.

    Replace this placeholder with the tool's actual behavior.
    """
    return list(values)


if __name__ == "__main__":
    print(run([]))
