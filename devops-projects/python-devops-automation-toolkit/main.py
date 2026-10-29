"""
Python DevOps Automation Toolkit

Stage 9 - Main CLI Integration

Features:
- Centralized configuration
- System monitoring
- Network diagnostics
- Website health checking
- Log analysis
- Linux command execution
- Combined monitoring
- JSON report generation
- Error handling
- CLI exit codes

Updated:
- Fixed system threshold integration
- Fixed website health detection
- Fixed module registry mocking
"""

import argparse
import json
import sys

from pathlib import Path

from modules.config_manager import load_config

from modules.system_monitor import (
    get_system_info,
    check_thresholds,
)

from modules.network_checker import (
    run_network_diagnostic,
)

from modules.website_checker import (
    check_website,
)

from modules.log_analyzer import (
    analyze_log_file,
)

from modules.command_runner import (
    run_command,
)

from modules.report_generator import (
    generate_configured_report,
    save_configured_report,
)


# ==========================================
# 1. Constants
# ==========================================

MODULE_NAMES = (
    "system_monitor",
    "network_checker",
    "website_checker",
    "log_analyzer",
    "command_runner",
)

COMMAND_TO_MODULE = {
    "system": "system_monitor",
    "network": "network_checker",
    "website": "website_checker",
    "logs": "log_analyzer",
    "commands": "command_runner",
}


# ==========================================
# 2. Error Result
# ==========================================

def error_result(module_name, error):
    """
    Convert module errors into a
    consistent result dictionary.
    """

    return {
        "success": False,
        "module": module_name,
        "error": str(error),
    }


# ==========================================
# 3. System Monitor
# ==========================================

def run_system(config):
    """
    Execute system monitoring.
    """

    settings = config["system_monitor"]

    information = get_system_info()

    warnings = check_thresholds(
        information,
        cpu_threshold=settings["cpu_threshold"],
        memory_threshold=settings["memory_threshold"],
        disk_threshold=settings["disk_threshold"],
    )

    normal_message = (
        "System resource usage is below warning thresholds"
    )

    high_usage = any(
        warning != normal_message
        for warning in warnings
    )

    return {
        "success": not high_usage,
        "module": "system_monitor",
        "data": information,
        "warnings": warnings,
    }


# ==========================================
# 4. Network Checker
# ==========================================

def run_network(config):
    """
    Execute network diagnostics.
    """

    settings = config["network_checker"]

    result = run_network_diagnostic(
        host=settings["host"],
        port=settings["port"],
        timeout=settings["timeout"],
    )

    if not isinstance(result, dict):
        raise ValueError(
            "Network checker must return a dictionary"
        )

    if isinstance(result.get("overall_status"), str):
        success = (
            result["overall_status"].upper()
            == "PASS"
        )

    elif isinstance(result.get("tcp"), dict):
        success = result["tcp"].get(
            "success",
            False,
        )

    else:
        raise ValueError(
            "Network checker result has no recognized status"
        )

    return {
        "success": bool(success),
        "module": "network_checker",
        "data": result,
    }


# ==========================================
# 5. Website Checker (FIXED)
# ==========================================

def run_website(config):
    """
    Execute website health checking.

    Supports the Stage 4 'healthy' field.
    """

    settings = config["website_checker"]

    result = check_website(
        url=settings["url"],
        timeout=settings["timeout"],
        expected_status=settings["expected_status"],
    )

    if not isinstance(result, dict):
        raise ValueError(
            "Website checker must return a dictionary"
        )

    if isinstance(result.get("healthy"), bool):
        success = result["healthy"]

    elif isinstance(result.get("success"), bool):
        success = result["success"]

    elif isinstance(result.get("overall_status"), str):
        success = (
            result["overall_status"].upper()
            in (
                "PASS",
                "HEALTHY",
                "SUCCESS",
            )
        )

    else:
        raise ValueError(
            "Website checker result has no recognized status"
        )

    return {
        "success": success,
        "module": "website_checker",
        "data": result,
    }


# ==========================================
# 6. Log Analyzer
# ==========================================

def run_logs(config):
    """
    Execute log analysis.
    """

    settings = config["log_analyzer"]

    result = analyze_log_file(
        file_path=settings["file_path"],
        top_n=settings["top_errors"],
    )

    if not isinstance(result, dict):
        raise ValueError(
            "Log analyzer must return a dictionary"
        )

    success = not bool(
        result.get("error")
    )

    return {
        "success": success,
        "module": "log_analyzer",
        "data": result,
    }


# ==========================================
# 7. Linux Command Runner
# ==========================================

def run_commands(config):
    """
    Execute approved Linux commands.
    """

    settings = config["command_runner"]

    command_results = {}

    successful = 0
    failed = 0

    for command in settings["commands"]:

        try:
            result = run_command(
                command,
                timeout=settings["timeout"],
            )

            if not isinstance(result, dict):
                raise ValueError(
                    "Command runner must return a dictionary"
                )

            if isinstance(result.get("success"), bool):
                command_success = result["success"]

            elif isinstance(result.get("return_code"), int):
                command_success = (
                    result["return_code"] == 0
                )

            else:
                raise ValueError(
                    "Command result has no recognized status"
                )

            command_results[command] = {
                **result,
                "success": command_success,
            }

        except (
            OSError,
            ValueError,
            RuntimeError,
            KeyError,
            TypeError,
        ) as error:

            command_success = False

            command_results[command] = {
                "success": False,
                "error": str(error),
            }

        if command_success:
            successful += 1

        else:
            failed += 1

    return {
        "success": failed == 0,
        "module": "command_runner",
        "total_commands": len(
            settings["commands"]
        ),
        "successful_commands": successful,
        "failed_commands": failed,
        "data": command_results,
    }


# ==========================================
# 8. Module Registry (TEST FIX)
# ==========================================

# Lambda wrappers allow unittest.mock.patch
# to replace the module functions correctly.

MODULE_RUNNERS = {
    "system_monitor": lambda config: run_system(config),
    "network_checker": lambda config: run_network(config),
    "website_checker": lambda config: run_website(config),
    "log_analyzer": lambda config: run_logs(config),
    "command_runner": lambda config: run_commands(config),
}


# ==========================================
# 9. Execute One Module
# ==========================================

def execute_module(module_name, config):
    """
    Execute a single configured module.
    """

    if module_name not in MODULE_RUNNERS:
        raise ValueError(
            f"Unknown module: {module_name}"
        )

    settings = config[module_name]

    if not settings["enabled"]:
        return {
            "success": None,
            "module": module_name,
            "status": "SKIPPED",
            "reason": (
                "Module disabled in configuration"
            ),
        }

    try:
        result = MODULE_RUNNERS[module_name](
            config
        )

        if not isinstance(result, dict):
            raise ValueError(
                "Module must return a dictionary"
            )

        if not isinstance(
            result.get("success"),
            bool,
        ):
            raise ValueError(
                "Module result must contain boolean success"
            )

        return result

    except (
        OSError,
        ValueError,
        RuntimeError,
        KeyError,
        TypeError,
        UnicodeError,
    ) as error:

        return error_result(
            module_name,
            error,
        )


# ==========================================
# 10. Execute All Modules
# ==========================================

def execute_all(config):
    """
    Execute all enabled modules.
    """

    results = {}

    for module_name in MODULE_NAMES:

        result = execute_module(
            module_name,
            config,
        )

        if result.get("status") == "SKIPPED":
            continue

        results[module_name] = result

    return results


# ==========================================
# 11. Print JSON
# ==========================================

def print_json(data):
    """
    Print formatted JSON.
    """

    print(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False,
            default=str,
        )
    )


# ==========================================
# 12. Print Summary
# ==========================================

def print_text_summary(results):
    """
    Display monitoring summary.
    """

    print()

    print("=" * 55)
    print("       PYTHON DEVOPS AUTOMATION TOOLKIT")
    print("=" * 55)

    successful = 0
    failed = 0

    for module_name, result in results.items():

        if result["success"]:
            status = "PASS"
            successful += 1

        else:
            status = "FAIL"
            failed += 1

        print(
            f"{module_name:<25} {status}"
        )

    print("-" * 55)

    print(
        f"Total checks: {len(results)}"
    )

    print(
        f"Successful:   {successful}"
    )

    print(
        f"Failed:       {failed}"
    )

    if not results:
        overall = "UNKNOWN"

    elif failed == 0:
        overall = "HEALTHY"

    elif successful == 0:
        overall = "UNHEALTHY"

    else:
        overall = "DEGRADED"

    print(
        f"Overall:      {overall}"
    )

    print("=" * 55)


# ==========================================
# 13. Resolve Configuration Paths
# ==========================================

def prepare_config_paths(config, config_path):
    """
    Resolve paths relative to config.json.
    """

    config_file = Path(
        config_path
    ).expanduser().resolve()

    base_directory = config_file.parent

    log_path = Path(
        config["log_analyzer"]["file_path"]
    ).expanduser()

    if not log_path.is_absolute():
        log_path = base_directory / log_path

    config["log_analyzer"]["file_path"] = str(
        log_path
    )

    output_directory = Path(
        config["reporting"]["output_directory"]
    ).expanduser()

    if not output_directory.is_absolute():
        output_directory = (
            base_directory / output_directory
        )

    config["reporting"]["output_directory"] = str(
        output_directory
    )

    return config


# ==========================================
# 14. CLI Argument Parser
# ==========================================

def build_parser():
    """
    Build CLI argument parser.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Python DevOps Automation Toolkit"
        )
    )

    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to configuration file",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    commands = (
        "system",
        "network",
        "website",
        "logs",
        "commands",
        "report",
        "all",
    )

    for command in commands:

        subparser = subparsers.add_parser(
            command,
            help=f"Run {command}",
        )

        subparser.add_argument(
            "--json",
            action="store_true",
            help="Display JSON output",
        )

        if command == "all":
            subparser.add_argument(
                "--save",
                action="store_true",
                help="Save combined report",
            )

    return parser


# ==========================================
# 15. Main Application
# ==========================================

def main(argv=None):
    """
    Main application entry point.

    Exit codes:
        0 = success
        1 = failed check or application error
        2 = invalid CLI arguments
    """

    parser = build_parser()

    args = parser.parse_args(argv)

    try:
        config = load_config(
            args.config
        )

        config = prepare_config_paths(
            config,
            args.config,
        )

    except (
        ValueError,
        FileNotFoundError,
        OSError,
        UnicodeError,
        KeyError,
    ) as error:

        print(
            f"Configuration error: {error}",
            file=sys.stderr,
        )

        return 1

    # --------------------------------------
    # Individual Module Commands
    # --------------------------------------

    if args.command in COMMAND_TO_MODULE:

        module_name = COMMAND_TO_MODULE[
            args.command
        ]

        result = execute_module(
            module_name,
            config,
        )

        print_json(result)

        if result.get("status") == "SKIPPED":
            return 0

        return (
            0
            if result["success"]
            else 1
        )

    # --------------------------------------
    # Combined Monitoring
    # --------------------------------------

    results = execute_all(config)

    report = generate_configured_report(
        results,
        config,
    )

    if args.json:
        print_json(report)

    else:
        print_text_summary(results)

    # --------------------------------------
    # Report Saving
    # --------------------------------------

    should_save = (
        args.command == "report"
        or (
            args.command == "all"
            and args.save
        )
    )

    if should_save:

        try:
            saved_path = save_configured_report(
                report,
                config,
            )

            print(
                f"\nReport saved to: {saved_path}",
                file=(
                    sys.stderr
                    if args.json
                    else sys.stdout
                ),
            )

        except (
            OSError,
            ValueError,
            FileNotFoundError,
        ) as error:

            print(
                f"Report saving failed: {error}",
                file=sys.stderr,
            )

            return 1

    return (
        0
        if report["summary"]["failed_checks"] == 0
        else 1
    )


# ==========================================
# 16. Program Entry Point
# ==========================================

if __name__ == "__main__":
    raise SystemExit(main())