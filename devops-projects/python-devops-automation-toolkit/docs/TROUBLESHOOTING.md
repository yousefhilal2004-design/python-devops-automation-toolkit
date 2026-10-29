# Troubleshooting Guide

## 1. Virtual Environment Not Activated

Activate the environment:

```bash
source .venv/bin/activate
```

Verify:

```bash
which python
```

The path should point to the project's `.venv` directory.

## 2. Missing Python Dependency

Install runtime dependencies:

```bash
python -m pip install -r requirements.txt
```

For development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

## 3. Coverage Module Not Found

Error:

```text
No module named coverage
```

Solution:

```bash
.venv/bin/python -m pip install coverage
```

## 4. Ruff Not Found

Install:

```bash
python -m pip install ruff
```

Verify:

```bash
ruff --version
```

## 5. Permission Denied When Running the Quality Script

```bash
chmod +x scripts/run_quality_checks.sh
```

Then:

```bash
./scripts/run_quality_checks.sh
```

## 6. Website Health Check Fails

Check:

- Internet connectivity
- Website URL
- Expected HTTP status code
- Timeout configuration

Run:

```bash
python main.py website
```

A failed health check does not necessarily indicate an application bug.

## 7. Network Diagnostics Fail

Verify the configured host and port.

Example:

```bash
python main.py network
```

Some networks block ICMP traffic or specific TCP ports.

## 8. Log File Not Found

Run:

```bash
python main.py all
```

Then:

```bash
ls -lh logs/
```

Check that the application has permission to write to the log directory.

## 9. JSON Output Is Invalid

Run:

```bash
python main.py --no-console-log all --json > reports/latest.json
```

Validate:

```bash
python -m json.tool reports/latest.json
```

## 10. Git Push Fails

Check the remote:

```bash
git remote -v
```

Check the branch:

```bash
git branch --show-current
```

Check the working tree:

```bash
git status
```

Verify your SSH authentication if using an SSH remote.

## 11. Automated Tests Fail

Run:

```bash
python -m unittest discover -s tests -v
```

Read the traceback and identify the failing test.

Investigate the underlying issue before changing application code or test expectations.