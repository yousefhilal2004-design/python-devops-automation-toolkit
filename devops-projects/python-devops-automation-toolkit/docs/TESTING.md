# Testing and Quality Assurance

## Overview

The project uses automated tests and static analysis to verify application behavior.

## Install Development Dependencies

```bash
python -m pip install -r requirements-dev.txt
```

## Run All Tests

```bash
python -m unittest discover -s tests -v
```

## Run CLI Tests

```bash
python -m unittest tests.test_main -v
```

## Run Logging Tests

```bash
python -m unittest tests.test_logging_manager -v
python -m unittest tests.test_logging_integration -v
```

## Run Stage 11 Tests

```bash
python -m unittest \
    tests.test_stage11_modules \
    tests.test_stage11_cli \
    tests.test_stage11_quality \
    -v
```

## Measure Test Coverage

```bash
python -m coverage run \
    --source=main,modules \
    -m unittest discover -s tests
```

Generate a terminal report:

```bash
python -m coverage report -m
```

Generate an HTML report:

```bash
python -m coverage html
```

The HTML report is created in `htmlcov/`.

## Static Analysis

```bash
ruff check .
```

## Automated Quality Script

```bash
./scripts/run_quality_checks.sh
```

The script performs:

1. Python version verification.
2. Syntax checks.
3. Automated tests.
4. Static analysis.
5. Coverage measurement.

## Testing Strategy

The project includes:

- Unit tests
- Module integration tests
- CLI integration tests
- Error-handling tests
- Logging tests
- Subprocess tests

External services are mocked where appropriate so automated tests do not depend on live network availability.

## Coverage Interpretation

Coverage measures executed code, not overall correctness.

A high coverage percentage does not guarantee that an application is free of bugs.

Tests should prioritize realistic success and failure scenarios.