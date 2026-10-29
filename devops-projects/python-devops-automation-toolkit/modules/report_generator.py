"""
Report Generator Module

Python DevOps Automation Toolkit

Features:
- Generate structured JSON reports
- Combine results from DevOps modules
- Calculate health summaries
- Generate unique report identifiers
- Save reports to files
- Handle report-writing errors
- Use configuration settings
- Command-line interface

Stage 8
"""

import argparse
import json
import os
import tempfile
import uuid

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from modules.config_manager import load_config


# ==========================================
# 1. Constants
# ==========================================

DEFAULT_REPORT_DIRECTORY = "reports"

SUPPORTED_FORMATS = {"json"}


# ==========================================
# 2. Generate Timestamp
# ==========================================

def generate_timestamp():
    """
    Return the current UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()


# ==========================================
# 3. Generate Unique Report ID
# ==========================================

def generate_report_id():
    """
    Generate a unique report identifier.

    Uses:
    - UTC timestamp
    - Random UUID component
    """

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%S%fZ")

    unique_part = uuid.uuid4().hex[:8]

    return f"{timestamp}-{unique_part}"


# ==========================================
# 4. Validate Module Results
# ==========================================

def validate_results(results):
    """
    Validate the results dictionary.

    Each module result must be a dictionary
    containing a boolean 'success' field.

    Returns a deep copy of validated results.
    """

    if not isinstance(results, dict):
        raise ValueError(
            "Results must be a dictionary"
        )

    validated = {}

    for module_name, module_result in results.items():

        if (
            not isinstance(module_name, str)
            or not module_name.strip()
        ):
            raise ValueError(
                "Module names must be non-empty strings"
            )

        if not isinstance(module_result, dict):
            raise ValueError(
                f"Result for '{module_name}' "
                "must be a dictionary"
            )

        if "success" not in module_result:
            raise ValueError(
                f"Result for '{module_name}' "
                "must contain 'success'"
            )

        if not isinstance(
            module_result["success"],
            bool,
        ):
            raise ValueError(
                f"'success' for '{module_name}' "
                "must be a boolean"
            )

        validated[module_name] = deepcopy(
            module_result
        )

    return validated


# ==========================================
# 5. Generate Health Summary
# ==========================================

def generate_summary(results):
    """
    Calculate the overall health summary.
    """

    validated = validate_results(results)

    total_checks = len(validated)

    successful_checks = sum(
        result["success"]
        for result in validated.values()
    )

    failed_checks = (
        total_checks - successful_checks
    )

    if total_checks == 0:
        overall_status = "UNKNOWN"

    elif failed_checks == 0:
        overall_status = "HEALTHY"

    elif successful_checks == 0:
        overall_status = "UNHEALTHY"

    else:
        overall_status = "DEGRADED"

    failed_modules = [
        module_name
        for module_name, result in validated.items()
        if not result["success"]
    ]

    success_percentage = (
        round(
            successful_checks / total_checks * 100,
            2,
        )
        if total_checks > 0
        else 0.0
    )

    return {
        "total_checks": total_checks,
        "successful_checks": successful_checks,
        "failed_checks": failed_checks,
        "success_percentage": success_percentage,
        "overall_status": overall_status,
        "failed_modules": failed_modules,
    }


# ==========================================
# 6. Generate Complete Report
# ==========================================

def generate_report(
    results,
    application="Python DevOps Automation Toolkit",
    environment="development",
):
    """
    Generate a structured report.

    This function does not write files.
    """

    validated = validate_results(results)

    if not isinstance(application, str):
        raise ValueError(
            "Application name must be a string"
        )

    if not application.strip():
        raise ValueError(
            "Application name cannot be empty"
        )

    if environment not in (
        "development",
        "testing",
        "production",
    ):
        raise ValueError(
            "Invalid environment"
        )

    report = {
        "report_id": generate_report_id(),
        "generated_at": generate_timestamp(),
        "application": application.strip(),
        "environment": environment,
        "summary": generate_summary(validated),
        "results": validated,
    }

    return report


# ==========================================
# 7. Validate Report Structure
# ==========================================

def validate_report(report):
    """
    Validate the main report structure.
    """

    if not isinstance(report, dict):
        raise ValueError(
            "Report must be a dictionary"
        )

    required_fields = (
        "report_id",
        "generated_at",
        "application",
        "environment",
        "summary",
        "results",
    )

    for field in required_fields:

        if field not in report:
            raise ValueError(
                f"Missing report field: {field}"
            )

    if not isinstance(report["report_id"], str):
        raise ValueError(
            "Report ID must be a string"
        )

    if not isinstance(report["summary"], dict):
        raise ValueError(
            "Report summary must be a dictionary"
        )

    validated_results = validate_results(
        report["results"]
    )

    expected_summary = generate_summary(
        validated_results
    )

    if report["summary"] != expected_summary:
        raise ValueError(
            "Report summary does not match results"
        )

    # Ensure JSON serialization is possible.
    try:
        json.dumps(report)

    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Report is not JSON serializable: {error}"
        ) from error

    return deepcopy(report)


# ==========================================
# 8. Create Report Directory
# ==========================================

def ensure_report_directory(
    directory=DEFAULT_REPORT_DIRECTORY,
):
    """
    Create the report directory if missing.
    """

    if (
        not isinstance(directory, (str, Path))
        or not str(directory).strip()
    ):
        raise ValueError(
            "Report directory must be a valid path"
        )

    path = Path(directory).expanduser()

    path.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not path.is_dir():
        raise ValueError(
            "Report path is not a directory"
        )

    return path


# ==========================================
# 9. Save Report
# ==========================================

def save_report(
    report,
    output_directory=DEFAULT_REPORT_DIRECTORY,
    report_format="json",
):
    """
    Save a report as JSON.

    Uses a temporary file and atomic replacement
    to reduce the risk of partial report files.

    Returns the saved report path.
    """

    if report_format not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported report format: {report_format}"
        )

    validated = validate_report(report)

    directory = ensure_report_directory(
        output_directory
    )

    report_id = validated["report_id"]

    # Prevent report IDs from becoming file paths.
    if (
        not report_id
        or not all(
            character.isalnum()
            or character in "-_"
            for character in report_id
        )
    ):
        raise ValueError(
            "Report ID contains invalid characters"
        )

    filename = f"report_{report_id}.json"

    destination = directory / filename

    if destination.exists():
        raise FileExistsError(
            f"Report already exists: {destination}"
        )

    temporary_path = None

    try:
        # Create the temporary file in the same
        # directory as the destination.
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=directory,
            prefix=".report_tmp_",
            suffix=".json",
            delete=False,
        ) as temporary_file:

            temporary_path = Path(
                temporary_file.name
            )

            json.dump(
                validated,
                temporary_file,
                indent=4,
                ensure_ascii=False,
            )

            temporary_file.write("\n")

            temporary_file.flush()

            os.fsync(
                temporary_file.fileno()
            )

        # Create the final file without overwriting
        # an existing report with the same ID.
        os.link(
            temporary_path,
            destination,
        )

        return destination

    except OSError as error:
        raise OSError(
            f"Failed to save report: {error}"
        ) from error

    finally:
        if (
            temporary_path is not None
            and temporary_path.exists()
        ):
            temporary_path.unlink()


# ==========================================
# 10. Load Saved Report
# ==========================================

def load_report(file_path):
    """
    Load and validate a saved JSON report.
    """

    path = Path(file_path).expanduser()

    if not path.is_file():
        raise FileNotFoundError(
            f"Report file not found: {path}"
        )

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            report = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid report JSON: {error.msg}"
        ) from error

    return validate_report(report)


# ==========================================
# 11. Generate Report From Configuration
# ==========================================

def generate_configured_report(
    results,
    config,
):
    """
    Generate a report using application settings.
    """

    application = config["application"]

    return generate_report(
        results=results,
        application=application["name"],
        environment=application["environment"],
    )


# ==========================================
# 12. Save Report From Configuration
# ==========================================

def save_configured_report(
    report,
    config,
):
    """
    Save a report using reporting settings.
    """

    reporting = config["reporting"]

    return save_report(
        report=report,
        output_directory=reporting["output_directory"],
        report_format=reporting["format"],
    )


# ==========================================
# 13. Sample Diagnostic Results
# ==========================================

def get_sample_results():
    """
    Return sample results for Stage 8 testing.

    These are demonstration values,
    not real system measurements.
    """

    return {
        "system_monitor": {
            "success": True,
            "cpu_percent": 25.0,
            "memory_percent": 40.0,
            "disk_percent": 30.0,
            "warnings": [],
        },

        "network_checker": {
            "success": True,
            "host": "example.com",
            "port": 443,
            "dns_success": True,
            "tcp_success": True,
        },

        "website_checker": {
            "success": True,
            "url": "https://example.com",
            "status_code": 200,
            "response_time_ms": 120.5,
        },

        "log_analyzer": {
            "success": True,
            "total_lines": 20,
            "error_count": 5,
            "warning_count": 3,
        },

        "command_runner": {
            "success": True,
            "total_commands": 8,
            "successful_commands": 8,
            "failed_commands": 0,
        },
    }


# ==========================================
# 14. Command-Line Interface
# ==========================================

def main():
    """
    Demonstrate report generation.

    Stage 9 will connect real module results.
    """

    parser = argparse.ArgumentParser(
        description="DevOps Toolkit Report Generator"
    )

    parser.add_argument(
        "--config",
        default="config.json",
        help="Configuration file path",
    )

    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the generated report",
    )

    parser.add_argument(
        "--summary",
        action="store_true",
        help="Display only the report summary",
    )

    args = parser.parse_args()

    try:
        config = load_config(
            args.config
        )

        # Stage 8 demonstration data.
        results = get_sample_results()

        report = generate_configured_report(
            results,
            config,
        )

        if args.summary:
            print(
                json.dumps(
                    report["summary"],
                    indent=4,
                )
            )

        else:
            print(
                json.dumps(
                    report,
                    indent=4,
                )
            )

        if args.save:
            saved_path = save_configured_report(
                report,
                config,
            )

            print(
                f"\nReport saved to: {saved_path}"
            )

        return 0

    except (
        ValueError,
        FileNotFoundError,
        OSError,
        UnicodeError,
        KeyError,
    ) as error:

        parser.exit(
            status=1,
            message=f"Report error: {error}\n",
        )


# ==========================================
# 15. Program Entry Point
# ==========================================

if __name__ == "__main__":
    raise SystemExit(main())