"""
Safe Linux Command Runner

Python DevOps Automation Toolkit

Features:
- Predefined read-only Linux commands
- Command allowlist
- subprocess execution without a shell
- stdout and stderr capture
- Exit code handling
- Execution time measurement
- Command timeouts
- Structured JSON results
- Command-line interface
"""

import argparse
import json
import math
import subprocess
import time

from datetime import datetime, timezone


# ==========================================
# 1. Approved Linux Commands
# ==========================================

ALLOWED_COMMANDS = {
    "whoami": ["whoami"],
    "hostname": ["hostname"],
    "uptime": ["uptime"],
    "disk": ["df", "-h", "/"],
    "memory": ["free", "-h"],
    "kernel": ["uname", "-a"],
    "network": ["ip", "-brief", "address"],
    "ports": ["ss", "-tuln"],
}


# ==========================================
# 2. Validate Command
# ==========================================

def validate_command(command):
    """
    Validate command against the allowlist.

    Returns the command name.
    """

    if not isinstance(command, str):
        raise ValueError("Command must be a string")

    command = command.strip()

    if command not in ALLOWED_COMMANDS:
        raise ValueError(
            f"Command '{command}' is not allowed. "
            f"Available commands: "
            f"{', '.join(ALLOWED_COMMANDS)}"
        )

    return command


# ==========================================
# 3. Validate Timeout
# ==========================================

def validate_timeout(timeout):
    """
    Validate execution timeout.
    """

    if isinstance(timeout, bool):
        raise ValueError("Timeout must be a number")

    try:
        timeout = float(timeout)
    except (TypeError, ValueError):
        raise ValueError(
            "Timeout must be a number"
        ) from None

    if not math.isfinite(timeout) or not 0 < timeout <= 60:
        raise ValueError(
            "Timeout must be greater than 0 and at most 60"
        )

    return timeout


# ==========================================
# 4. Execute Approved Command
# ==========================================

def run_command(command, timeout=5):
    """
    Execute an approved Linux command.

    Returns a structured dictionary.
    """

    command = validate_command(command)
    timeout = validate_timeout(timeout)

    arguments = ALLOWED_COMMANDS[command].copy()

    result = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "command": command,
        "arguments": arguments,
        "success": False,
        "return_code": None,
        "stdout": "",
        "stderr": "",
        "execution_time_ms": None,
        "error": None,
    }

    start_time = time.perf_counter()

    try:
        completed = subprocess.run(
            arguments,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
            check=False,
        )

        elapsed = time.perf_counter() - start_time

        result.update({
            "success": completed.returncode == 0,
            "return_code": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "execution_time_ms": round(
                elapsed * 1000,
                2,
            ),
        })

        if completed.returncode != 0:
            result["error"] = (
                "Command returned a nonzero exit code"
            )

    except subprocess.TimeoutExpired:
        result["error"] = "Command execution timed out"

    except FileNotFoundError:
        result["error"] = (
            "Required Linux command was not found"
        )

    except PermissionError:
        result["error"] = (
            "Permission denied while executing command"
        )

    except OSError:
        result["error"] = (
            "Operating system error while executing command"
        )

    finally:
        if result["execution_time_ms"] is None:
            elapsed = time.perf_counter() - start_time

            result["execution_time_ms"] = round(
                elapsed * 1000,
                2,
            )

    return result


# ==========================================
# 5. Run All Approved Commands
# ==========================================

def run_all_commands(timeout=5):
    """
    Execute all approved diagnostic commands.
    """

    timeout = validate_timeout(timeout)

    results = {}

    for command in ALLOWED_COMMANDS:
        results[command] = run_command(
            command,
            timeout,
        )

    successful = sum(
        item["success"]
        for item in results.values()
    )

    total = len(results)

    return {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_commands": total,
        "successful_commands": successful,
        "failed_commands": total - successful,
        "overall_status": (
            "PASS" if successful == total else "FAIL"
        ),
        "results": results,
    }


# ==========================================
# 6. Command-Line Interface
# ==========================================

def main():
    """
    Run approved Linux diagnostics from terminal.
    """

    parser = argparse.ArgumentParser(
        description="Safe Linux Command Runner"
    )

    parser.add_argument(
        "--command",
        choices=[*ALLOWED_COMMANDS, "all"],
        required=True,
        help="Approved diagnostic command",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=5,
        help="Execution timeout in seconds",
    )

    args = parser.parse_args()

    try:
        if args.command == "all":
            result = run_all_commands(
                timeout=args.timeout
            )

            success = (
                result["overall_status"] == "PASS"
            )

        else:
            result = run_command(
                command=args.command,
                timeout=args.timeout,
            )

            success = result["success"]

    except ValueError as error:
        parser.error(str(error))

    print(json.dumps(result, indent=4))

    return 0 if success else 1


# ==========================================
# 7. Program Entry Point
# ==========================================

if __name__ == "__main__":
    raise SystemExit(main())