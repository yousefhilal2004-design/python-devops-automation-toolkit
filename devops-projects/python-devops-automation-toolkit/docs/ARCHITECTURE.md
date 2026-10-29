# System Architecture

## Overview

The Python DevOps Automation Toolkit uses a modular architecture.

Each diagnostic feature is implemented in a separate Python module. The main CLI coordinates configuration loading, module execution, logging, and reporting.

## Architecture Diagram

```text
                   USER / TERMINAL
                          |
                          v
                       main.py
                          |
                +---------+---------+
                |                   |
                v                   v
         Configuration         Logging Manager
            Manager                  |
                |                    v
                |              logs/toolkit.log
                |
                v
          Module Dispatcher
                |
      +---------+---------+---------+
      |         |         |         |
      v         v         v         v
   System    Network   Website     Log
   Monitor   Checker   Checker   Analyzer
      |
      +-----------------------------+
                                    |
                                    v
                              Command Runner
                                    |
                                    v
                              Module Results
                                    |
                                    v
                              Report Generator
                                    |
                                    v
                              JSON / Terminal
```

The diagram illustrates the logical flow. The command runner is an independent module, not a dependency of the system monitor.

## Main Components

### 1. Main CLI

File: `main.py`

Responsibilities:

- Parse command-line arguments.
- Load configuration.
- Initialize logging.
- Select and execute modules.
- Handle module failures.
- Generate combined reports.
- Return meaningful exit codes.

### 2. Configuration Manager

File: `modules/config_manager.py`

Responsibilities:

- Load JSON configuration.
- Validate configuration settings.
- Provide configuration values to the application.

### 3. System Monitor

File: `modules/system_monitor.py`

Responsibilities:

- Collect CPU, memory, disk, and uptime information.
- Compare resource usage against configured thresholds.
- Return structured monitoring results.

### 4. Network Checker

File: `modules/network_checker.py`

Responsibilities:

- Perform network diagnostics.
- Check connectivity to configured targets.
- Return structured results.

### 5. Website Checker

File: `modules/website_checker.py`

Responsibilities:

- Perform HTTP/HTTPS health checks.
- Evaluate website availability.
- Return website status information.

### 6. Log Analyzer

File: `modules/log_analyzer.py`

Responsibilities:

- Read configured log files.
- Analyze log entries.
- Produce structured summaries.

### 7. Command Runner

File: `modules/command_runner.py`

Responsibilities:

- Execute approved Linux commands.
- Capture command output.
- Report command success or failure.

### 8. Report Generator

File: `modules/report_generator.py`

Responsibilities:

- Combine monitoring results.
- Calculate summary statistics.
- Save reports in the configured format.

### 9. Logging Manager

File: `modules/logging_manager.py`

Responsibilities:

- Configure application logging.
- Record module execution events.
- Support multiple log levels.
- Rotate log files.
- Record exception types.

## Execution Flow

When the user runs:

```bash
python main.py all
```

The application:

1. Parses CLI arguments.
2. Loads and validates configuration.
3. Initializes application logging.
4. Executes each enabled monitoring module.
5. Records module execution results.
6. Generates a combined report.
7. Displays the summary.
8. Returns an exit code.

When `--save` is supplied, the application also saves the report.

## Error Handling

Module execution failures are converted into standardized results.

A failure in one module should not prevent the remaining enabled modules from running.

Individual modules report their own success or failure, while the combined report summarizes the overall result.

## Design Principles

- Separation of concerns
- Reusable modules
- Configuration-driven execution
- Consistent result structures
- Defensive error handling
- Testability
- Clear command-line interfaces

## Future Architecture Improvements

Possible extensions include containerization, scheduled execution, alerting integrations, and metrics export.