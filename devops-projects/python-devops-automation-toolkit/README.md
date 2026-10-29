# Python DevOps Automation Toolkit

A modular Python command-line application for Linux system monitoring, network diagnostics, website health checks, log analysis, and safe command execution.

The toolkit combines several common DevOps tasks into a single application with configurable settings, structured reports, professional logging, and automated tests.

## Overview

DevOps engineers frequently need to monitor system resources, investigate connectivity problems, inspect application logs, and automate routine Linux operations.

This project demonstrates how these tasks can be implemented using Python and organized into a reusable command-line toolkit.

The application is designed primarily for Linux environments and was developed using Ubuntu under Windows Subsystem for Linux (WSL2).

## Key Features

### 1. System Monitoring

Collects information about:

- CPU utilization
- Memory usage
- Disk usage
- System uptime
- Operating system details

Supports configurable CPU, memory, and disk warning thresholds.

### 2. Network Diagnostics

Performs network connectivity checks using configurable hosts, ports, and timeouts.

Useful for investigating basic network availability and service connectivity.

### 3. Website Health Checking

Checks HTTP/HTTPS website availability and compares responses with an expected HTTP status code.

### 4. Log Analysis

Analyzes application log files and produces structured results to assist with troubleshooting.

### 5. Safe Linux Command Execution

Runs a predefined set of approved Linux diagnostic commands.

Commands are selected from an allowlist rather than accepting arbitrary shell commands.

### 6. Configuration Management

Uses a centralized JSON configuration file to control monitoring settings, targets, thresholds, and report output.

### 7. JSON Report Generation

Combines module results into structured reports that can be consumed by other automation tools.

### 8. Professional Logging

Provides:

- UTC timestamps
- Configurable log levels
- File and console logging
- Log rotation
- Module execution tracking
- Exception logging

### 9. Automated Testing

Includes unit tests, integration tests, CLI tests, and quality-assurance checks.

## Technologies

- Python
- Linux / Ubuntu
- WSL2
- Bash
- Git and GitHub
- JSON
- Python `unittest`
- Python `logging`
- Coverage.py
- Ruff
- GitHub Actions

## Project Structure

```text
python-devops-automation-toolkit/
├── main.py
├── config.json
├── requirements.txt
├── requirements-dev.txt
├── modules/
├── tests/
├── scripts/
├── docs/
├── sample_logs/
├── logs/
├── reports/
└── .github/workflows/
```

## Installation

Clone the repository:

```bash
git clone git@github.com:yousefhilal2004-design/python-devops-automation-toolkit.git
```

Enter the project:

```bash
cd python-devops-automation-toolkit
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install runtime dependencies:

```bash
python -m pip install -r requirements.txt
```

For development and testing:

```bash
python -m pip install -r requirements-dev.txt
```

See [Installation Guide](docs/INSTALLATION.md) for more information.

## Usage

Display help:

```bash
python main.py --help
```

Run system monitoring:

```bash
python main.py system
```

Run network diagnostics:

```bash
python main.py network
```

Check website availability:

```bash
python main.py website
```

Analyze logs:

```bash
python main.py logs
```

Run approved Linux commands:

```bash
python main.py commands
```

Execute all enabled modules:

```bash
python main.py all
```

Generate a report:

```bash
python main.py report
```

Save a combined report:

```bash
python main.py all --save
```

Display JSON output:

```bash
python main.py all --json
```

Enable debug logging:

```bash
python main.py --log-level DEBUG all
```

Disable console logging:

```bash
python main.py --no-console-log all
```

See [Usage Guide](docs/USAGE.md) for additional examples.

## Configuration

The application uses `config.json`.

Configuration includes:

- Monitoring thresholds
- Network targets
- Website URLs
- Command execution settings
- Log analysis settings
- Report output settings

See [Configuration Guide](docs/CONFIGURATION.md).

## Testing

Run all automated tests:

```bash
python -m unittest discover -s tests -v
```

Run the quality-assurance script:

```bash
./scripts/run_quality_checks.sh
```

Measure test coverage:

```bash
python -m coverage run --source=main,modules -m unittest discover -s tests
python -m coverage report -m
```

Run static analysis:

```bash
ruff check .
```

See [Testing Guide](docs/TESTING.md).

## Logging

Application logs are stored by default in:

```text
logs/toolkit.log
```

View recent events:

```bash
tail -n 30 logs/toolkit.log
```

Follow logs in real time:

```bash
tail -f logs/toolkit.log
```

Generated logs and reports are excluded from Git.

## CLI Exit Codes

| Code | Meaning |
|---|---|
| `0` | Successful execution or all enabled checks passed |
| `1` | Failed monitoring check or application error |
| `2` | Invalid command-line arguments |

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Installation](docs/INSTALLATION.md)
- [Usage](docs/USAGE.md)
- [Configuration](docs/CONFIGURATION.md)
- [Testing](docs/TESTING.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## Project Purpose

This project was developed as a practical DevOps learning project to strengthen skills in:

- Python automation
- Linux administration
- Network troubleshooting
- Application monitoring
- Modular software design
- Error handling
- Automated testing
- Git-based development workflows

## Future Improvements

Potential enhancements include:

- Docker packaging
- Scheduled monitoring
- Email or messaging alerts
- Metrics export
- CI/CD deployment workflows
- Integration with monitoring platforms

These are planned improvements, not features currently implemented.

## Author

**Yousef Ayed Hilal**

Computer Engineering Student — Birzeit University

DevOps Engineering Enthusiast

GitHub: [yousefhilal2004-design](https://github.com/yousefhilal2004-design)

## License

MIT License. See [LICENSE](LICENSE).