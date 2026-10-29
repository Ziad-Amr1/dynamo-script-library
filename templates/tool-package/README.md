# {{name}}

**Category:** `{{category}}`  
**Version:** `{{version}}`  
**Python engine:** {{python_engine}}

## Overview

{{description}}

Explain the problem this tool solves, who it is for, and the expected outcome.
State clearly whether it is a Dynamo graph, a Python node, or a standalone
script.

## Features

- List each user-visible capability.
- Keep claims specific and testable.
- Remove features that are not implemented.

## Requirements

| Requirement | Details |
| --- | --- |
| Revit | Not yet verified. Record the versions you tested. |
| Dynamo | Not yet verified. Record the versions you tested. |
| Python engine | {{python_engine}} |
| Dynamo packages | None, or list package name and minimum version. |
| Other dependencies | None, or list them. |

## Installation

1. Download this folder from the repository or from a release package.
2. Place the folder somewhere permanent; do not run files from inside a ZIP.
3. Install any Dynamo packages listed above through
   **Packages > Manage Packages** in Dynamo.
4. Open the entry point listed below.

## Usage

Describe the steps in order, assuming the reader is new to Dynamo:

1. Open the Revit project to use and keep a backup copy.
2. Open Dynamo and load the graph, or open the Python node and paste the script.
3. Set the inputs described in the next section.
4. Run the graph and inspect the outputs.
5. Save the model or undo if the result is not correct.

### Entry points

- `script.py`

## Inputs and Outputs

| Direction | Name | Type | Description |
| --- | --- | --- | --- |
| Input | `values` | list | Describe the expected values and an example. |
| Output | `result` | list | Describe the result and an example. |

## Warnings and Limitations

- State whether the tool modifies the Revit model.
- Describe what it does not handle.
- Mention model backup and test-on-a-copy requirements.
- Do not claim support for versions that have not been tested.

## Troubleshooting

| Symptom | Likely cause | Resolution |
| --- | --- | --- |
| Example error message | Example cause | Example fix |

## Version History

See [CHANGELOG.md](CHANGELOG.md). The current version is `{{version}}`.

## License

This tool is part of the Dynamo Script Library and is licensed under the
[MIT License](../../../LICENSE). See the repository
[licensing notes](../../../docs/LICENSING.md) for third-party components.
