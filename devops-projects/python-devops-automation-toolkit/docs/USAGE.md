# CLI Usage Guide

## Overview

The toolkit provides a command-line interface through `main.py`.

## Display Help

```bash
python main.py --help
```

## Available Commands

| Command | Purpose |
|---|---|
| `system` | Monitor Linux system resources |
| `network` | Run network diagnostics |
| `website` | Check website health |
| `logs` | Analyze application logs |
| `commands` | Execute approved Linux commands |
| `all` | Execute all enabled modules |
| `report` | Execute modules and save a report |

## Examples

### System Monitoring

```bash
python main.py system
```

### Network Diagnostics

```bash
python main.py network
```

### Website Health Check

```bash
python main.py website
```

### Log Analysis

```bash
python main.py logs
```

### Linux Commands

```bash
python main.py commands
```

### Combined Monitoring

```bash
python main.py all
```

### Generate and Save a Report

```bash
python main.py report
```

### Save a Combined Report

```bash
python main.py all --save
```

### JSON Output

```bash
python main.py all --json
```

### Debug Logging

```bash
python main.py --log-level DEBUG all
```

### Custom Log File

```bash
python main.py --log-file logs/custom.log network
```

### Disable Console Logging

```bash
python main.py --no-console-log all
```

### Custom Configuration File

```bash
python main.py --config custom-config.json all
```

Global options such as `--config` and `--log-level` must appear before the subcommand.

## Exit Codes

| Exit code | Meaning |
|---|---|
| `0` | Success |
| `1` | Failed check or application error |
| `2` | Invalid CLI arguments |

## Bash Automation Example

```bash
#!/usr/bin/env bash

if python main.py all; then
    echo "All monitoring checks passed"
else
    echo "One or more monitoring checks failed"
fi
```

## JSON Processing

Save JSON output:

```bash
python main.py --no-console-log all --json > reports/latest.json
```

Validate JSON:

```bash
python -m json.tool reports/latest.json
```

The monitoring command may return exit code `1` while still producing valid JSON when a health check fails.