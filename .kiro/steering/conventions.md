---
inclusion: always
---

# Development Conventions

## Package Management

**Always use `uv` as the package manager.** Never use pip, conda, or other package managers.

```bash
# Add dependency
uv add package-name

# Remove dependency
uv remove package-name

# Sync dependencies
uv sync
```

## Code Cleanup

### Test Scripts

**Always delete test scripts after use.** Test scripts are temporary tools for validation and should not clutter the codebase.

- Scripts matching `test_*.py` should be deleted once testing is complete
- Scripts matching `debug_*.py` should be removed after debugging
- Scripts matching `check_*.py` should be cleaned up after validation

### Documentation

**Do not create .md documentation files for each change.** The codebase already has excessive documentation files like:
- `compare_ui.md`
- `UPDATE_B8_B9.md`
- `UI_UX_IMPROVEMENTS.md`
- `CLAUDE.md`

Only update existing documentation files when necessary. Do not create new markdown files to document changes or summaries.

## Refactoring

**Always apply refactoring when working with code.** This includes:

- Consolidating duplicate code into reusable functions
- Removing unused imports and variables
- Improving variable and function names for clarity
- Extracting complex logic into well-named helper functions
- Simplifying nested conditionals
- Following Python best practices (PEP 8)

## Code Style

- Use type hints for function parameters and return values
- Use docstrings for modules, classes, and functions
- Keep functions focused and single-purpose
- Use meaningful variable names (avoid single letters except in loops)
- Prefer f-strings for string formatting
- Use pathlib.Path for file operations

## Logging

- Use Python's logging module (already configured in most scripts)
- Log levels: INFO for normal operations, WARNING for issues, ERROR for failures
- Include context in log messages (file names, field names, values)

## Indonesian Language Support

- All text extraction and cleaning patterns must support Indonesian language
- Month names should be in Indonesian (Januari, Februari, etc.)
- Field names follow Indonesian tax document terminology
- OCR must use Indonesian + English language packs
