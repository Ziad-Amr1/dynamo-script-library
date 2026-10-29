# Downloading and installing tools

This guide is for users who have never used Git or GitHub. You do not need to
install Git, use a terminal, or understand branches to download and run a tool.

## Choose a download method

| I need... | Use this | Skill level |
| --- | --- | --- |
| One tool, ready to extract | A release package (`.zip` asset) | Beginner |
| The entire library | **Code > Download ZIP** on the repository page | Beginner |
| One `.py` or `.dyn` file | The **Download raw file** button on the file page | Beginner |
| A stable, documented snapshot | The [Releases](https://github.com/Ziad-Amr1/dynamo-script-library/releases) page | Beginner |
| To contribute changes | `git clone` | Developer |

## Option 1: Download the whole library as a ZIP

1. Open the repository page:
   https://github.com/Ziad-Amr1/dynamo-script-library
2. Select the green **Code** button.
3. Select **Download ZIP**.
4. Save the file, usually to your **Downloads** folder.
5. Right-click the ZIP and choose **Extract All**. On macOS, double-click the
   ZIP. Do not work from inside the ZIP preview.
6. Move the extracted folder to a permanent location, for example
   `C:\DynamoTools\dynamo-script-library`.

Direct link to the current `main` branch ZIP:

https://github.com/Ziad-Amr1/dynamo-script-library/archive/refs/heads/main.zip

> **Tip:** `main` changes over time. For production work, prefer a release
> package so you can return to the same version later.

## Option 2: Download one tool from a release

1. Open the [Releases](https://github.com/Ziad-Amr1/dynamo-script-library/releases)
   page.
2. Open the newest release.
3. Under **Assets**, download the ZIP named after the tool and version, for
   example `text-find-replace-v0.1.0.zip`.
4. Extract the ZIP. It creates one folder named after the tool.
5. Keep that folder intact. The files inside depend on each other.

Release assets are built from the tagged source code and include a
`PACKAGE_MANIFEST.json` with version and file hashes.

### Optional: verify a download (Windows)

1. Download `SHA256SUMS.txt` from the same release.
2. Open PowerShell in the download folder.
3. Run:

   ```powershell
   Get-FileHash .\text-find-replace-v0.1.0.zip -Algorithm SHA256
   ```

4. Compare the hash with the matching line in `SHA256SUMS.txt`. They must match
   exactly. If they do not, delete the file and download it again.

## Option 3: Download a single file

1. Open the tool folder in the repository, for example
   `scripts/utilities/text-find-replace/`.
2. Open the file, such as `script.py`.
3. Select the **Download raw file** button (the download arrow near the top
   right of the file).
4. Save the file where you can find it.

> **Caution:** a single file may depend on other files in its folder. If the
> tool README lists multiple entry points, download the whole folder or a
> release package instead.

## Option 4: Clone the repository (developers)

Use this only if you have Git installed and want to contribute or track changes:

```powershell
git clone https://github.com/Ziad-Amr1/dynamo-script-library.git
```

## Where to put tool files

- Use a permanent local folder, for example
  `C:\DynamoTools\<tool-id>\`.
- Avoid running files directly from a ZIP, a temporary folder, or a synced
  OneDrive path that may move while Dynamo is running.
- Keep each tool in its own folder so updates do not mix files.
- Do not rename files that `script.json` lists as entry points.

## Open a tool in Revit and Dynamo

1. Open Autodesk Revit.
2. Save a backup copy of the model you will test with.
3. Go to **Manage > Dynamo**.
4. In Dynamo, choose **File > Open** and select the tool's `.dyn` file, **or**
   for a Python-only tool, create a **Python Script** node and follow the
   tool README.
5. Install required Dynamo packages with **Packages > Manage Packages**. The
   package name and minimum version are listed in the tool README and
   `script.json`.
6. Set the Python engine if needed. In Dynamo, select the Python node and use
   the engine selector. Many newer tools require **CPython 3**; IronPython 2.7
   tools use older syntax.
7. Run the graph. Inspect warnings and outputs before saving the model.
8. If the result is wrong, use **Undo** or close without saving and restore
   your backup.

## Updating a tool

1. Download the newer release package.
2. Keep the old folder until you have tested the new version.
3. Extract the new version to a new folder, for example
   `text-find-replace-v0.2.0`.
4. Read the tool's `CHANGELOG.md` for breaking changes.
5. Update any Dynamo file paths that point to the old folder.

## Common download problems

| Problem | Resolution |
| --- | --- |
| The ZIP will not open | Re-download it; the download may be incomplete. Use **Extract All**, not a preview window. |
| Windows says the file is blocked | Right-click the ZIP, open **Properties**, tick **Unblock**, then extract again. |
| The folder contains `__MACOSX` | That is harmless metadata from macOS ZIP creation; ignore it. |
| I cannot find the **Code** button | Make sure you are on the repository home page, not inside a single file. |
| A release has no tool ZIP | The release may not have packaged that tool. Use the repository ZIP or open an issue. |
| Dynamo cannot find custom nodes | Install the missing package through **Manage Packages**. |

Still stuck? See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or open an issue using
the bug report form.
