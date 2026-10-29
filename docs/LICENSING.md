# Licensing

## Repository license

This repository is licensed under the [MIT License](../LICENSE).

The repository owner selected MIT on 2026-10-29. This document records that
decision and explains how to handle third-party material; it is not legal
advice.

MIT is permissive: others may use, copy, modify, merge, publish, distribute,
sublicense, and sell copies, provided the copyright notice and permission notice
are included. The software is provided without warranty.

## What the MIT license covers

- Original source code, Dynamo graphs, documentation, and templates in this
  repository.
- Original examples, unless a file states otherwise.

It does not automatically cover:

- Third-party Dynamo packages that users install separately.
- Autodesk software, APIs, sample content, or trademarks.
- Revit models, families, or datasets owned by others.

## Third-party components

Do not add third-party code, packages, images, or sample models unless:

1. The license allows redistribution in this repository.
2. Required copyright and license notices are preserved.
3. The dependency is documented in the tool README and `script.json`.

Prefer not to vendor third-party code. List the package as a dependency and let
users install it through Dynamo's package manager or `pip` in their own
environment.

If a tool requires a Dynamo package, record its name and the version you tested.
Do not redistribute the package inside a tool ZIP unless its license explicitly
allows it and the license text is included.

## Autodesk material

- Do not commit Autodesk installers, proprietary libraries, or licensed sample
  content.
- Do not state or imply Autodesk endorsement.
- Revit and Dynamo are trademarks of Autodesk, Inc.
- Users are responsible for complying with their Autodesk license terms when
  running automation against Revit.

## Contributions

By submitting a contribution, you confirm that you have the right to license it
under the repository's MIT License and that it contains no confidential or
third-party material that conflicts with that license.

If a contribution includes third-party material, call it out in the pull
request, include the license text, and update the tool README.

## Tool-level notices

Every tool README ends with a License section pointing to the repository license.
If a specific tool has a different license, its README must state that clearly
and include the full license text. No such tool exists at the time of writing.

## Questions

If the intended licensing terms are unclear for a new tool or dependency, stop
and ask the repository owner before publishing. Do not silently choose a license.
