```markdown
# repo-intelligence-hub Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches the core development patterns and conventions used in the `repo-intelligence-hub` Python codebase. You'll learn how to structure files, write imports and exports, follow commit message conventions, and write and locate tests. This guide is ideal for contributors aiming for consistency and maintainability in this repository.

## Coding Conventions

### File Naming
- **Style:** kebab-case
- **Example:**  
  ```
  data-processor.py
  utils/helper-functions.py
  ```

### Import Style
- **Style:** Relative imports
- **Example:**
  ```python
  from .utils import data_cleaner
  from ..models import report_generator
  ```

### Export Style
- **Style:** Named exports (explicitly specifying what is available for import)
- **Example:**
  ```python
  __all__ = ['analyze_data', 'generate_report']
  ```

### Commit Messages
- **Type:** Mixed, with feature commits prefixed by `feat`
- **Example:**
  ```
  feat: add data aggregation module
  fix: correct typo in report generator
  ```

## Workflows

### Adding a New Feature
**Trigger:** When implementing a new capability or module  
**Command:** `/add-feature`

1. Create a new Python file using kebab-case (e.g., `new-feature.py`)
2. Use relative imports for any shared utilities or models
3. Define named exports with `__all__`
4. Write a test file named `new-feature.test.py` in the same or a `tests/` directory
5. Commit changes with a message starting with `feat:`
6. Push your branch and open a pull request

### Refactoring Existing Code
**Trigger:** When improving code structure or readability  
**Command:** `/refactor`

1. Identify the target file(s) for refactoring
2. Maintain kebab-case naming if renaming files
3. Update relative imports as needed
4. Ensure all named exports are still valid
5. Update or add corresponding test files (`*.test.py`)
6. Commit with a descriptive message (e.g., `refactor: simplify data loader`)
7. Push changes and open a pull request

### Running Tests
**Trigger:** Before merging or after making changes  
**Command:** `/run-tests`

1. Locate all test files matching `*.test.*`
2. Run tests using the repository's preferred method (test framework is currently unknown; try `pytest` or `unittest`)
   ```bash
   pytest
   # or
   python -m unittest discover
   ```
3. Review test results and fix any failures

## Testing Patterns

- **Test File Naming:**  
  Test files follow the pattern `*.test.*` (e.g., `data-processor.test.py`)
- **Framework:**  
  Unknown (try `pytest` or `unittest`)
- **Example Test File:**
  ```python
  # data-processor.test.py
  import unittest
  from .data-processor import analyze_data

  class TestDataProcessor(unittest.TestCase):
      def test_analyze_data(self):
          result = analyze_data([1, 2, 3])
          self.assertEqual(result, 6)
  ```

## Commands
| Command       | Purpose                                   |
|---------------|-------------------------------------------|
| /add-feature  | Scaffold and commit a new feature module  |
| /refactor     | Refactor code following conventions       |
| /run-tests    | Run all test files in the repository      |
```