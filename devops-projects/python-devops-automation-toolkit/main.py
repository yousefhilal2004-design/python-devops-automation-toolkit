"""
Python DevOps Automation Toolkit

Stage 10 - Professional Logging & Error Handling

Features:
- Centralized configuration
- System monitoring
- Network diagnostics
- Website health checking
- Log analysis
- Safe Linux command execution
- Combined monitoring
- JSON report generation
- Professional application logging
- Module execution timing
- Error handling
- CLI exit codes
"""

import argparse
import json
import sys
import time

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

from modules.logging_manager import (
    setup_logging,
    get_logger,
    log_module_start,
    log_module_result,
    log_module_exception,
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
# 2. Application Logger
# ==========================================

logger = get_logger()


# ==========================================
# 3. Standardized Error Result
# ==========================================

def error_result(module_name, error):
    """
    Convert module errors into a consistent
    result dictionary.

    Preserves the Stage 9 result structure.
    """

    return {
        "success": False,
        "module": module_name,
        "error": str(error),
    }


# ==========================================
# 4. System Monitor
# ==========================================

def run_system(config):
    """
    Execute system monitoring.

    Uses thresholds from config.json.
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
# 5. Network Checker
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

    if isinstance(
        result.get("overall_status"),
        str,
    ):
        success = (
            result["overall_status"].upper()
            == "PASS"
        )

    elif isinstance(
        result.get("tcp"),
        dict,
    ):
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
# 6. Website Checker
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

    if isinstance(
        result.get("healthy"),
        bool,
    ):
        success = result["healthy"]

    elif isinstance(
        result.get("success"),
        bool,
    ):
        success = result["success"]

    elif isinstance(
        result.get("overall_status"),
        str,
    ):
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
# 7. Log Analyzer
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
# 8. Linux Command Runner
# ==========================================

def run_commands(config):
    """
    Execute approved Linux commands.

    Individual command failures do not
    stop the remaining commands.
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

            if isinstance(
                result.get("success"),
                bool,
            ):
                command_success = result["success"]

            elif isinstance(
                result.get("return_code"),
                int,
            ):
                command_success = (
                    result["return_code"] == 0
                )

            elif isinstance(
                result.get("returncode"),
                int,
            ):
                command_success = (
                    result["returncode"] == 0
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

            logger.error(
                "Command execution failed: %s",
                type(error).__name__,
            )

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
# 9. Module Registry
# ==========================================

# Lambda wrappers preserve compatibility
# with unittest.mock.patch in Stage 9 tests.

MODULE_RUNNERS = {
    "system_monitor": lambda config: run_system(config),
    "network_checker": lambda config: run_network(config),
    "website_checker": lambda config: run_website(config),
    "log_analyzer": lambda config: run_logs(config),
    "command_runner": lambda config: run_commands(config),
}


# ==========================================
# 10. Execute One Module
# ==========================================

def execute_module(module_name, config):
    """
    Execute one configured module.

    Features:
    - Disabled module handling
    - Execution timing
    - Logging
    - Result validation
    - Exception handling
    """

    if module_name not in MODULE_RUNNERS:
        raise ValueError(
            f"Unknown module: {module_name}"
        )

    settings = config[module_name]

    if not settings["enabled"]:

        logger.info(
            "Module %s skipped: disabled",
            module_name,
        )

        return {
            "success": None,
            "module": module_name,
            "status": "SKIPPED",
            "reason": (
                "Module disabled in configuration"
            ),
        }

    log_module_start(
        logger,
        module_name,
    )

    start_time = time.perf_counter()

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

        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        log_module_result(
            logger,
            module_name,
            result["success"],
            duration_ms,
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

        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        log_module_exception(
            logger,
            module_name,
            error,
        )

        logger.debug(
            "Module %s failed after %.2f ms",
            module_name,
            duration_ms,
        )

        return error_result(
            module_name,
            error,
        )


# ==========================================
# 11. Execute All Modules
# ==========================================

def execute_all(config):
    """
    Execute all enabled modules.

    Disabled modules are excluded
    from the combined report.
    """

    logger.info(
        "Starting combined monitoring"
    )

    results = {}

    for module_name in MODULE_NAMES:

        result = execute_module(
            module_name,
            config,
        )

        if result.get("status") == "SKIPPED":
            continue

        results[module_name] = result

    successful = sum(
        1
        for result in results.values()
        if result["success"]
    )

    failed = len(results) - successful

    logger.info(
        "Combined monitoring finished: "
        "%d successful, %d failed",
        successful,
        failed,
    )

    return results


# ==========================================
# 12. Print JSON
# ==========================================

def print_json(data):
    """
    Display formatted JSON.
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
# 13. Print Text Summary
# ==========================================

def print_text_summary(results):
    """
    Display monitoring results in
    a readable terminal format.
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
# 14. Resolve Configuration Paths
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
# 15. CLI Argument Parser
# ==========================================

def build_parser():
    """
    Build CLI argument parser.

    Includes Stage 10 logging options.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Python DevOps Automation Toolkit"
        )
    )

    # --------------------------------------
    # Configuration
    # --------------------------------------

    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to configuration file",
    )

    # --------------------------------------
    # Logging Options
    # --------------------------------------

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=[
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ],
        help="Application logging level",
    )

    parser.add_argument(
        "--log-file",
        default=None,
        help="Custom application log file",
    )

    parser.add_argument(
        "--no-console-log",
        action="store_true",
        help="Disable console logging",
    )

    # --------------------------------------
    # Commands
    # --------------------------------------

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
# 16. Main Application
# ==========================================

def main(argv=None):
    """
    Main application entry point.

    Exit codes:
        0 = Success
        1 = Failed check or application error
        2 = Invalid CLI arguments
    """

    parser = build_parser()

    args = parser.parse_args(argv)

    # --------------------------------------
    # Load Configuration
    # --------------------------------------

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
    # Initialize Logging
    # --------------------------------------

    if args.log_file is None:

        config_directory = Path(
            args.config
        ).expanduser().resolve().parent

        log_file = (
            config_directory
            / "logs"
            / "toolkit.log"
        )

    else:
        log_file = Path(
            args.log_file
        ).expanduser()

    try:
        setup_logging(
            log_file=log_file,
            level=args.log_level,
            max_bytes=1_000_000,
            backup_count=3,
            console=not args.no_console_log,
        )

    except (
        OSError,
        ValueError,
    ) as error:

        print(
            "Logging initialization failed: "
            f"{type(error).__name__}",
            file=sys.stderr,
        )

        return 1

    logger.info(
        "Application started"
    )

    logger.debug(
        "Selected command: %s",
        args.command,
    )

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
            logger.info(
                "Application finished: module skipped"
            )
            return 0

        exit_code = (
            0
            if result["success"]
            else 1
        )

        logger.info(
            "Application finished with exit code %d",
            exit_code,
        )

        return exit_code

    # --------------------------------------
    # Combined Monitoring
    # --------------------------------------

    results = execute_all(
        config
    )

    try:
        report = generate_configured_report(
            results,
            config,
        )

    except (
        OSError,
        ValueError,
        RuntimeError,
        KeyError,
        TypeError,
    ) as error:

        logger.error(
            "Report generation failed: %s",
            type(error).__name__,
        )

        print(
            "Report generation failed: "
            f"{type(error).__name__}",
            file=sys.stderr,
        )

        return 1

    if args.json:
        print_json(
            report
        )

    else:
        print_text_summary(
            results
        )

    # --------------------------------------
    # Save Report
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

            logger.info(
                "Report saved successfully"
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

            logger.error(
                "Report saving failed: %s",
                type(error).__name__,
            )

            print(
                f"Report saving failed: {error}",
                file=sys.stderr,
            )

            return 1

    # --------------------------------------
    # Final Exit Code
    # --------------------------------------

    exit_code = (
        0
        if report["summary"]["failed_checks"] == 0
        else 1
    )

    logger.info(
        "Application finished with exit code %d",
        exit_code,
    )

    return exit_code


# ==========================================
# 17. Program Entry Point
# ==========================================

if __name__ == "__main__":
    raise SystemExit(main())