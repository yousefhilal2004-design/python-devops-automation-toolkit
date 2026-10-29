"""
Log Analyzer Module

Python DevOps Automation Toolkit

Features:
- Read application log files
- Parse timestamps, levels, and messages
- Count log levels
- Extract errors
- Identify frequent errors
- Calculate error and warning percentages
- Detect malformed log lines
- Find first and last timestamps
- Generate JSON reports
- Handle file errors
- Command-line interface
"""

import argparse
import json
import re

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


# ==========================================
# 1. Supported Log Levels
# ==========================================

LOG_LEVELS = (
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
)


# ==========================================
# 2. Regular Expression Pattern
# ==========================================

LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} "
    r"\d{2}:\d{2}:\d{2}) "
    r"(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL) "
    r"(?P<message>.*)$"
)


# ==========================================
# 3. Validate Log File
# ==========================================

def validate_log_file(file_path):
    """
    Validate that the log file exists and is readable.
    """

    path = Path(file_path).expanduser()

    if not path.exists():
        raise FileNotFoundError(
            f"Log file does not exist: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a regular file: {path}"
        )

    return path


# ==========================================
# 4. Parse a Single Log Line
# ==========================================

def parse_log_line(line):
    """
    Parse a log line into:
    - timestamp
    - level
    - message

    Returns None for malformed lines.
    """

    match = LOG_PATTERN.match(line.strip())

    if not match:
        return None

    timestamp_text = match.group("timestamp")

    try:
        parsed_timestamp = datetime.strptime(
            timestamp_text,
            "%Y-%m-%d %H:%M:%S",
        )
    except ValueError:
        return None

    return {
        "timestamp": parsed_timestamp.isoformat(
            sep=" "
        ),
        "level": match.group("level"),
        "message": match.group("message"),
    }


# ==========================================
# 5. Calculate Percentage
# ==========================================

def calculate_percentage(count, total):
    """
    Calculate a percentage safely.
    """

    if total == 0:
        return 0.0

    return round((count / total) * 100, 2)


# ==========================================
# 6. Analyze Log File
# ==========================================

def analyze_log_file(file_path, top_n=5):
    """
    Analyze a log file and return a structured report.
    """

    path = validate_log_file(file_path)

    if isinstance(top_n, bool) or not isinstance(top_n, int):
        raise ValueError("top_n must be an integer")

    if top_n < 1:
        raise ValueError("top_n must be at least 1")

    total_lines = 0
    valid_lines = 0
    malformed_lines = 0

    level_counts = Counter()

    error_messages = Counter()

    errors = []

    first_timestamp = None
    last_timestamp = None

    # Read file line by line
    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
    ) as log_file:

        for line_number, line in enumerate(
            log_file,
            start=1,
        ):

            total_lines += 1

            parsed = parse_log_line(line)

            if parsed is None:
                malformed_lines += 1
                continue

            valid_lines += 1

            level = parsed["level"]
            message = parsed["message"]
            timestamp = parsed["timestamp"]

            level_counts[level] += 1

            # Track earliest and latest timestamps
            if (
                first_timestamp is None
                or timestamp < first_timestamp
            ):
                first_timestamp = timestamp

            if (
                last_timestamp is None
                or timestamp > last_timestamp
            ):
                last_timestamp = timestamp

            # Collect ERROR and CRITICAL entries
            if level in ("ERROR", "CRITICAL"):

                error_messages[message] += 1

                errors.append({
                    "line_number": line_number,
                    "timestamp": timestamp,
                    "level": level,
                    "message": message,
                })

    # Ensure all log levels appear in output
    counts = {
        level: level_counts[level]
        for level in LOG_LEVELS
    }

    error_count = (
        counts["ERROR"]
        + counts["CRITICAL"]
    )

    warning_count = counts["WARNING"]

    top_errors = [
        {
            "message": message,
            "count": count,
        }
        for message, count in error_messages.most_common(
            top_n
        )
    ]

    # Build final report
    report = {
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "file": str(path),

        "summary": {
            "total_lines": total_lines,
            "valid_lines": valid_lines,
            "malformed_lines": malformed_lines,
            "log_levels": counts,
            "error_count": error_count,
            "warning_count": warning_count,
            "error_percentage": calculate_percentage(
                error_count,
                valid_lines,
            ),
            "warning_percentage": calculate_percentage(
                warning_count,
                valid_lines,
            ),
            "first_timestamp": first_timestamp,
            "last_timestamp": last_timestamp,
        },

        "top_errors": top_errors,

        "errors": errors,
    }

    return report


# ==========================================
# 7. Command-Line Interface
# ==========================================

def main():
    """
    Run log analysis from the terminal.
    """

    parser = argparse.ArgumentParser(
        description="Python DevOps Log Analyzer"
    )

    parser.add_argument(
        "--file",
        required=True,
        help="Path to application log file",
    )

    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of top errors to display",
    )

    args = parser.parse_args()

    try:
        result = analyze_log_file(
            args.file,
            top_n=args.top,
        )

    except (
        FileNotFoundError,
        ValueError,
        OSError,
    ) as error:
        parser.error(str(error))

    print(json.dumps(result, indent=4))

    return 0


# ==========================================
# 8. Program Entry Point
# ==========================================

if __name__ == "__main__":
    raise SystemExit(main())