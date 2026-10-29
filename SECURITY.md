# Security Policy

## Supported versions

Security fixes are applied to the latest published release and to the current
`main` branch. Older releases may not receive fixes. Each tool README states
the version it documents.

## Reporting a vulnerability

**Do not open a public issue for security problems.**

Report vulnerabilities privately through GitHub Security Advisories:

https://github.com/Ziad-Amr1/dynamo-script-library/security/advisories/new

Please include:

- The affected tool and version.
- Revit, Dynamo, and Python versions.
- Steps to reproduce the issue.
- Potential impact and any suggested mitigation.

You can expect an acknowledgement within seven days. Please allow time for a
fix and coordinated disclosure before publishing details.

## Security guidelines for contributors

- Never commit API keys, passwords, tokens, private project data, or customer
  model files.
- Do not include confidential Revit models, schedules, or exports in examples.
  Replace them with synthetic data.
- Dynamo graphs and Python nodes execute code. Review scripts before running
  them and state clearly when a tool modifies a model.
- Do not add third-party dependencies without checking their license and
  security posture.
- Report suspicious behavior in an existing tool using a private advisory.

## For users

Dynamo scripts can read and modify Revit models and can execute Python code.
Only run scripts you trust, review the graph before enabling Python nodes, and
test on a copy of your model before using a tool in production.
