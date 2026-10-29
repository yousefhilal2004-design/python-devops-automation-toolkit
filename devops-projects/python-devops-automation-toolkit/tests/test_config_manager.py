"""
Automated tests for Configuration Management.

Python DevOps Automation Toolkit
"""

import json
import tempfile
import unittest

from copy import deepcopy
from pathlib import Path

from modules.config_manager import (
    DEFAULT_CONFIG,
    get_config_section,
    load_config,
    save_config,
    validate_boolean,
    validate_config,
    validate_positive_integer,
    validate_text,
    validate_threshold,
)


# ==========================================
# 1. Basic Validation Tests
# ==========================================

class TestBasicValidation(unittest.TestCase):

    def test_valid_boolean(self):
        self.assertTrue(
            validate_boolean(True, "enabled")
        )

    def test_invalid_boolean(self):
        with self.assertRaises(ValueError):
            validate_boolean("true", "enabled")

    def test_valid_threshold(self):
        self.assertEqual(
            validate_threshold(80, "cpu"),
            80,
        )

    def test_threshold_zero(self):
        self.assertEqual(
            validate_threshold(0, "cpu"),
            0,
        )

    def test_threshold_100(self):
        self.assertEqual(
            validate_threshold(100, "cpu"),
            100,
        )

    def test_invalid_threshold(self):
        with self.assertRaises(ValueError):
            validate_threshold(150, "cpu")

    def test_negative_threshold(self):
        with self.assertRaises(ValueError):
            validate_threshold(-1, "cpu")

    def test_boolean_threshold(self):
        with self.assertRaises(ValueError):
            validate_threshold(True, "cpu")

    def test_valid_positive_integer(self):
        self.assertEqual(
            validate_positive_integer(5, "top_errors"),
            5,
        )

    def test_invalid_positive_integer(self):
        with self.assertRaises(ValueError):
            validate_positive_integer(0, "top_errors")

    def test_boolean_positive_integer(self):
        with self.assertRaises(ValueError):
            validate_positive_integer(True, "top_errors")

    def test_valid_text(self):
        self.assertEqual(
            validate_text(" DevOps ", "name"),
            "DevOps",
        )

    def test_empty_text(self):
        with self.assertRaises(ValueError):
            validate_text("", "name")


# ==========================================
# 2. Configuration Validation Tests
# ==========================================

class TestConfigurationValidation(unittest.TestCase):

    def setUp(self):
        self.config = deepcopy(DEFAULT_CONFIG)

    def test_valid_default_config(self):
        result = validate_config(self.config)

        self.assertEqual(
            result["application"]["name"],
            "Python DevOps Automation Toolkit",
        )

    def test_invalid_config_type(self):
        with self.assertRaises(ValueError):
            validate_config([])

    def test_missing_section(self):
        del self.config["network_checker"]

        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_missing_setting(self):
        del self.config["system_monitor"]["cpu_threshold"]

        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_invalid_cpu_threshold(self):
        self.config["system_monitor"]["cpu_threshold"] = 120

        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_invalid_network_port(self):
        self.config["network_checker"]["port"] = 70000

        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_invalid_network_host(self):
        self.config["network_checker"]["host"] = ""

        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_invalid_website_url(self):
        self.config["website_checker"]["url"] = "example.com"

        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_invalid_website_timeout(self):
        self.config["website_checker"]["timeout"] = -5

        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_invalid_expected_status(self):
        self.config["website_checker"]["expected_status"] = 700

        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_invalid_log_top_errors(self):
        self.config["log_analyzer"]["top_errors"] = 0

        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_invalid_command(self):
        self.config["command_runner"]["commands"] = [
            "unknown_command"
        ]

        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_duplicate_commands(self):
        self.config["command_runner"]["commands"] = [
            "uptime",
            "uptime",
        ]

        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_invalid_reporting_format(self):
        self.config["reporting"]["format"] = "xml"

        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_invalid_environment(self):
        self.config["application"]["environment"] = "unknown"

        with self.assertRaises(ValueError):
            validate_config(self.config)


# ==========================================
# 3. File Loading Tests
# ==========================================

class TestConfigurationLoading(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()

        self.config_path = (
            Path(self.temp_directory.name)
            / "config.json"
        )

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_load_valid_config(self):

        self.config_path.write_text(
            json.dumps(DEFAULT_CONFIG),
            encoding="utf-8",
        )

        result = load_config(self.config_path)

        self.assertEqual(
            result["network_checker"]["port"],
            443,
        )

    def test_missing_config_file(self):

        with self.assertRaises(FileNotFoundError):
            load_config(self.config_path)

    def test_missing_config_with_defaults(self):

        result = load_config(
            self.config_path,
            use_defaults=True,
        )

        self.assertEqual(
            result["system_monitor"]["cpu_threshold"],
            80,
        )

    def test_invalid_json(self):

        self.config_path.write_text(
            '{"cpu_threshold": 80,}',
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            load_config(self.config_path)

    def test_config_path_is_directory(self):

        with self.assertRaises(ValueError):
            load_config(self.temp_directory.name)


# ==========================================
# 4. Section Access Tests
# ==========================================

class TestConfigSections(unittest.TestCase):

    def test_get_valid_section(self):

        config = deepcopy(DEFAULT_CONFIG)

        result = get_config_section(
            config,
            "network_checker",
        )

        self.assertEqual(
            result["host"],
            "example.com",
        )

    def test_unknown_section(self):

        config = deepcopy(DEFAULT_CONFIG)

        with self.assertRaises(ValueError):
            get_config_section(
                config,
                "unknown",
            )

    def test_section_returns_copy(self):

        config = deepcopy(DEFAULT_CONFIG)

        result = get_config_section(
            config,
            "system_monitor",
        )

        result["cpu_threshold"] = 10

        self.assertEqual(
            config["system_monitor"]["cpu_threshold"],
            80,
        )


# ==========================================
# 5. Save Configuration Tests
# ==========================================

class TestSaveConfiguration(unittest.TestCase):

    def test_save_and_reload(self):

        with tempfile.TemporaryDirectory() as directory:

            path = Path(directory) / "config.json"

            config = deepcopy(DEFAULT_CONFIG)

            config["system_monitor"]["cpu_threshold"] = 75

            save_config(config, path)

            loaded = load_config(path)

            self.assertEqual(
                loaded["system_monitor"]["cpu_threshold"],
                75,
            )

    def test_reject_invalid_config_before_save(self):

        with tempfile.TemporaryDirectory() as directory:

            path = Path(directory) / "config.json"

            config = deepcopy(DEFAULT_CONFIG)

            config["network_checker"]["port"] = -1

            with self.assertRaises(ValueError):
                save_config(config, path)

            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()