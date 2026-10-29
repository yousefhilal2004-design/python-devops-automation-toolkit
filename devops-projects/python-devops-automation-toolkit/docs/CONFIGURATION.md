# Configuration Guide

## Overview

The toolkit uses `config.json` to manage monitoring settings.

Configuration is loaded through the configuration manager.

## Example Configuration

```json
{
    "application": {
        "name": "Python DevOps Automation Toolkit",
        "version": "1.0.0",
        "environment": "development"
    },
    "system_monitor": {
        "enabled": true,
        "cpu_threshold": 80,
        "memory_threshold": 85,
        "disk_threshold": 90
    },
    "network_checker": {
        "enabled": true,
        "host": "example.com",
        "port": 443,
        "timeout": 3
    },
    "website_checker": {
        "enabled": true,
        "url": "https://example.com",
        "timeout": 5,
        "expected_status": 200
    },
    "log_analyzer": {
        "enabled": true,
        "file_path": "sample_logs/application.log",
        "top_errors": 5
    },
    "command_runner": {
        "enabled": true,
        "commands": [
            "whoami",
            "hostname",
            "uptime"
        ],
        "timeout": 5
    },
    "reporting": {
        "output_directory": "reports",
        "format": "json"
    }
}
```

## System Monitoring

The following fields configure system resource monitoring:

| Field | Description |
|---|---|
| `enabled` | Enable or disable monitoring |
| `cpu_threshold` | CPU warning threshold |
| `memory_threshold` | Memory warning threshold |
| `disk_threshold` | Disk warning threshold |

## Network Checker

| Field | Description |
|---|---|
| `enabled` | Enable or disable network diagnostics |
| `host` | Target hostname |
| `port` | Target TCP port |
| `timeout` | Connection timeout in seconds |

## Website Checker

| Field | Description |
|---|---|
| `enabled` | Enable or disable website checks |
| `url` | Target website URL |
| `timeout` | Request timeout |
| `expected_status` | Expected HTTP status code |

## Log Analyzer

| Field | Description |
|---|---|
| `enabled` | Enable or disable log analysis |
| `file_path` | Log file to analyze |
| `top_errors` | Number of top errors to report |

## Command Runner

| Field | Description |
|---|---|
| `enabled` | Enable or disable command execution |
| `commands` | Approved command names |
| `timeout` | Command execution timeout |

Only commands supported by the command runner's allowlist can be executed.

## Reporting

| Field | Description |
|---|---|
| `output_directory` | Destination for generated reports |
| `format` | Report format |

## Custom Configuration

Run with a different configuration file:

```bash
python main.py --config custom-config.json all
```

Relative log-analysis and report paths are resolved relative to the configuration file location.

## Security Recommendations

- Do not store passwords or API tokens in committed configuration files.
- Avoid publishing private internal hostnames or network addresses.
- Review configuration changes before committing them.
- Use safe, non-sensitive examples in public documentation.