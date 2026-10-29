"""
Configuration Management Module

Python DevOps Automation Toolkit

Features:
- Load JSON configuration
- Validate configuration sections
- Validate thresholds and timeouts
- Validate network and website settings
- Validate log analyzer settings
- Validate command runner settings
- Provide default configuration
- Access individual configuration sections
- Command-line interface
"""

import argparse
import json
import math

from copy import deepcopy
from pathlib import Path

from modules.network_checker import (
    validate_host,
    validate_port,
    validate_timeout as validate_network_timeout,
)

from modules.website_checker import (
    validate_url,
    validate_timeout as validate_website_timeout,
    validate_expected_status,
)

from modules.command_runner import (
    ALLOWED_COMMANDS,
    validate_timeout as validate_command_timeout,
)


# ==========================================
# 1. Default Configuration
# ==========================================

DEFAULT_CONFIG = {
    "application": {
        "name": "Python DevOps Automation Toolkit",
        "version": "1.0.0",
        "environment": "development",
    },

    "system_monitor": {
        "enabled": True,
        "cpu_threshold": 80,
        "memory_threshold": 85,
        "disk_threshold": 90,
    },

    "network_checker": {
        "enabled": True,
        "host": "example.com",
        "port": 443,
        "timeout": 3,
    },

    "website_checker": {
        "enabled": True,
        "url": "https://example.com",
        "timeout": 5,
        "expected_status": 200,
    },

    "log_analyzer": {
        "enabled": True,
        "file_path": "sample_logs/application.log",
        "top_errors": 5,
    },

    "command_runner": {
        "enabled": True,
        "commands": list(ALLOWED_COMMANDS),
        "timeout": 5,
    },

    "reporting": {
        "output_directory": "reports",
        "format": "json",
    },
}


# ==========================================
# 2. Validate Boolean
# ==========================================

def validate_boolean(value, field_name):
    """
    Ensure a setting is a boolean.
    """

    if not isinstance(value, bool):
        raise ValueError(
            f"{field_name} must be true or false"
        )

    return value


# ==========================================
# 3. Validate Threshold
# ==========================================

def validate_threshold(value, field_name):
    """
    Validate a percentage threshold from 0 to 100.
    """

    if isinstance(value, bool):
        raise ValueError(
            f"{field_name} must be a number"
        )

    if not isinstance(value, (int, float)):
        raise ValueError(
            f"{field_name} must be a number"
        )

    if not math.isfinite(value) or not 0 <= value <= 100:
        raise ValueError(
            f"{field_name} must be between 0 and 100"
        )

    return value


# ==========================================
# 4. Validate Positive Integer
# ==========================================

def validate_positive_integer(value, field_name):
    """
    Validate a positive integer.
    """

    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(
            f"{field_name} must be an integer"
        )

    if value < 1:
        raise ValueError(
            f"{field_name} must be at least 1"
        )

    return value


# ==========================================
# 5. Validate Text
# ==========================================

def validate_text(value, field_name):
    """
    Validate a non-empty string.
    """

    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"{field_name} must be a non-empty string"
        )

    return value.strip()


# ==========================================
# 6. Validate Configuration
# ==========================================

def validate_config(config):
    """
    Validate the complete configuration.

    Returns a normalized copy.
    Raises ValueError for invalid settings.
    """

    if not isinstance(config, dict):
        raise ValueError(
            "Configuration must be a JSON object"
        )

    # Require all configuration sections
    for section in DEFAULT_CONFIG:

        if section not in config:
            raise ValueError(
                f"Missing configuration section: {section}"
            )

        if not isinstance(config[section], dict):
            raise ValueError(
                f"Section '{section}' must be an object"
            )

    # Require the expected settings in each section
    for section, defaults in DEFAULT_CONFIG.items():

        for key in defaults:

            if key not in config[section]:
                raise ValueError(
                    f"Missing configuration setting: "
                    f"{section}.{key}"
                )

    # Work with a copy
    validated = deepcopy(config)

    # --------------------------------------
    # Application
    # --------------------------------------

    app = validated["application"]

    app["name"] = validate_text(
        app["name"],
        "application.name",
    )

    app["version"] = validate_text(
        app["version"],
        "application.version",
    )

    app["environment"] = validate_text(
        app["environment"],
        "application.environment",
    )

    if app["environment"] not in (
        "development",
        "testing",
        "production",
    ):
        raise ValueError(
            "application.environment must be "
            "development, testing, or production"
        )

    # --------------------------------------
    # System Monitor
    # --------------------------------------

    system = validated["system_monitor"]

    system["enabled"] = validate_boolean(
        system["enabled"],
        "system_monitor.enabled",
    )

    for key in (
        "cpu_threshold",
        "memory_threshold",
        "disk_threshold",
    ):
        system[key] = validate_threshold(
            system[key],
            f"system_monitor.{key}",
        )

    # --------------------------------------
    # Network Checker
    # --------------------------------------

    network = validated["network_checker"]

    network["enabled"] = validate_boolean(
        network["enabled"],
        "network_checker.enabled",
    )

    network["host"] = validate_host(
        network["host"]
    )

    # JSON should contain an integer port
    if (
        isinstance(network["port"], bool)
        or not isinstance(network["port"], int)
    ):
        raise ValueError(
            "network_checker.port must be an integer"
        )

    network["port"] = validate_port(
        network["port"]
    )

    network["timeout"] = validate_network_timeout(
        network["timeout"]
    )

    # --------------------------------------
    # Website Checker
    # --------------------------------------

    website = validated["website_checker"]

    website["enabled"] = validate_boolean(
        website["enabled"],
        "website_checker.enabled",
    )

    website["url"] = validate_url(
        website["url"]
    )

    website["timeout"] = validate_website_timeout(
        website["timeout"]
    )

    if (
        website["expected_status"] is not None
        and (
            isinstance(website["expected_status"], bool)
            or not isinstance(
                website["expected_status"],
                int,
            )
        )
    ):
        raise ValueError(
            "website_checker.expected_status "
            "must be an integer or null"
        )

    website["expected_status"] = validate_expected_status(
        website["expected_status"]
    )

    # --------------------------------------
    # Log Analyzer
    # --------------------------------------

    logs = validated["log_analyzer"]

    logs["enabled"] = validate_boolean(
        logs["enabled"],
        "log_analyzer.enabled",
    )

    logs["file_path"] = validate_text(
        logs["file_path"],
        "log_analyzer.file_path",
    )

    logs["top_errors"] = validate_positive_integer(
        logs["top_errors"],
        "log_analyzer.top_errors",
    )

    # --------------------------------------
    # Command Runner
    # --------------------------------------

    commands = validated["command_runner"]

    commands["enabled"] = validate_boolean(
        commands["enabled"],
        "command_runner.enabled",
    )

    if not isinstance(commands["commands"], list):
        raise ValueError(
            "command_runner.commands must be a list"
        )

    if not commands["commands"]:
        raise ValueError(
            "command_runner.commands cannot be empty"
        )

    for command in commands["commands"]:

        if (
            not isinstance(command, str)
            or command not in ALLOWED_COMMANDS
        ):
            raise ValueError(
                f"Invalid command in configuration: {command}"
            )

    if len(set(commands["commands"])) != len(
        commands["commands"]
    ):
        raise ValueError(
            "command_runner.commands contains duplicates"
        )

    commands["timeout"] = validate_command_timeout(
        commands["timeout"]
    )

    # --------------------------------------
    # Reporting
    # --------------------------------------

    reporting = validated["reporting"]

    reporting["output_directory"] = validate_text(
        reporting["output_directory"],
        "reporting.output_directory",
    )

    if reporting["format"] != "json":
        raise ValueError(
            "Only JSON reporting is currently supported"
        )

    return validated


# ==========================================
# 7. Load Configuration
# ==========================================

def load_config(
    file_path="config.json",
    use_defaults=False,
):
    """
    Load and validate configuration from JSON.

    If the file is missing and use_defaults=True,
    return the default configuration.
    """

    path = Path(file_path).expanduser()

    if not path.exists():

        if use_defaults:
            return validate_config(
                deepcopy(DEFAULT_CONFIG)
            )

        raise FileNotFoundError(
            f"Configuration file not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Configuration path is not a file: {path}"
        )

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            config = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON configuration: {error.msg}"
        ) from error

    return validate_config(config)


# ==========================================
# 8. Get Configuration Section
# ==========================================

def get_config_section(config, section):
    """
    Return a copy of a configuration section.
    """

    if not isinstance(config, dict):
        raise ValueError(
            "Configuration must be a dictionary"
        )

    if section not in DEFAULT_CONFIG:
        raise ValueError(
            f"Unknown configuration section: {section}"
        )

    if section not in config:
        raise ValueError(
            f"Missing configuration section: {section}"
        )

    return deepcopy(config[section])


# ==========================================
# 9. Save Configuration
# ==========================================

def save_config(config, file_path):
    """
    Validate and save configuration as JSON.

    Use this only for trusted, non-secret settings.
    """

    validated = validate_config(config)

    path = Path(file_path).expanduser()

    if path.exists() and not path.is_file():
        raise ValueError(
            f"Configuration destination is not a file: {path}"
        )

    if not path.parent.is_dir():
        raise FileNotFoundError(
            f"Parent directory does not exist: {path.parent}"
        )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            validated,
            file,
            indent=4,
        )

        file.write("\n")

    return path


# ==========================================
# 10. Command-Line Interface
# ==========================================

def main():
    """
    Load and display configuration.
    """

    parser = argparse.ArgumentParser(
        description="DevOps Toolkit Configuration Manager"
    )

    parser.add_argument(
        "--file",
        default="config.json",
        help="Configuration file path",
    )

    parser.add_argument(
        "--section",
        choices=list(DEFAULT_CONFIG),
        help="Display one configuration section",
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate configuration without printing it",
    )

    parser.add_argument(
        "--use-defaults",
        action="store_true",
        help="Use defaults if the configuration file is missing",
    )

    args = parser.parse_args()

    try:
        config = load_config(
            args.file,
            use_defaults=args.use_defaults,
        )

        if args.validate:
            print("Configuration is valid")
            return 0

        if args.section:
            result = get_config_section(
                config,
                args.section,
            )
        else:
            result = config

        print(json.dumps(result, indent=4))

        return 0

    except (
        ValueError,
        FileNotFoundError,
        OSError,
        UnicodeError,
    ) as error:

        parser.exit(
            status=1,
            message=f"Configuration error: {error}\n",
        )


# ==========================================
# 11. Program Entry Point
# ==========================================

if __name__ == "__main__":
    raise SystemExit(main())