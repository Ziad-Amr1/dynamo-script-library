# Examples

Cross-tool examples that show how several scripts fit together in a real
workflow.

## What belongs here

- End-to-end example workflows that use two or more tools.
- Synthetic input data and expected output.
- Short explanations aimed at new users.
- Links to the tools involved.

Single-tool examples should live with the tool, especially when they are small
code snippets in its README.

## Suggested layout

```text
examples/
└── sheet-cleanup-workflow/
    ├── README.md
    ├── input/
    └── expected-output/
```

Do not add empty folders. Create the example when the content exists.

## Rules

- Use synthetic data only.
- Do not include `.rvt`, `.rfa`, or `.rte` files unless they are small,
  license-safe, and genuinely required.
- Document the Revit and Dynamo versions used to validate the example, or state
  that it is unverified.
- Keep example files small and deterministic.
