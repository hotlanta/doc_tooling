# doc-tooling

Shared documentation tooling for quality checks, validation, and content maintenance.

This repository contains reusable scripts and templates used across multiple
documentation repositories. It is intended to be consumed as a Git submodule
or subtree, not used standalone.

---

## What this repo is for

- Running Vale linting in a consistent way
- Validating generated PDF output (layout, tables, links)
- Performing DITA content audits and fixes
- Supporting local and pre-commit quality checks
- Providing reusable documentation engineering utilities

---

## What this repo is NOT

- A project-specific configuration repo
- A place for generated output or reports
- A CI pipeline definition
- A replacement for individual project documentation repos

---

## Repository structure

```text
bat/        Windows batch utilities (manual use)
powershell/ PowerShell automation (Vale, doc checks, hooks)
python/     Python-based analyzers and content tools
lefthook/   Lefthook configuration templates
```

---

## How this repository is used
This repository is typically added to a documentation project as a submodule:
```text
git submodule add <repo-url> tooling
```

Project-level scripts and hooks then invoke tooling from this repository, for example:
```bash
tooling\powershell\run-doc-checks.ps1
```

All scripts are designed to run relative to the calling project root.

---

## Python dependencies
Some tools require Python dependencies. Install them with:
```bash
pip install -r tooling/python/requirements.txt
```

---

## Versioning
This repository is versioned using Git tags.
Documentation projects should pin to a specific version and upgrade intentionally.

---

## License
See the LICENSE file for details.

