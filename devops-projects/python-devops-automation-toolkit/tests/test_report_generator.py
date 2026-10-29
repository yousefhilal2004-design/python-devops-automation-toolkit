"""
Automated tests for Report Generator.

Python DevOps Automation Toolkit
"""

import json
import tempfile
import unittest

from pathlib import Path

from modules.config_manager import DEFAULT_CONFIG

from modules.report_generator import (
    ensure_report_directory,
    generate_configured_report,
    generate_report,
    generate_report_id,
    generate_summary,
    generate_timestamp,
    get_sample_results,
    load_report,
    save_configured_report,
    save_report,
    validate_report,
    validate_results,
)


# ==========================================
# 1. Timestamp and ID Tests
# ==========================================

class TestReportIdentifiers(unittest.TestCase):

    def test_timestamp_is_string(self):
        result = generate_timestamp()

        self.assertIsInstance(result, str)

    def test_timestamp_contains_timezone(self):
        result = generate_timestamp()

        self.assertIn("+00:00", result)

    def test_report_id_is_string(self):
        result = generate_report_id()

        self.assertIsInstance(result, str)

    def test_report_ids_are_unique(self):
        first = generate_report_id()
        second = generate_report_id()

        self.assertNotEqual(first, second)


# ==========================================
# 2. Result Validation Tests
# ==========================================

class TestResultValidation(unittest.TestCase):

    def test_valid_results(self):
        results = {
            "network": {
                "success": True
            }
        }

        validated = validate_results(results)

        self.assertTrue(
            validated["network"]["success"]
        )

    def test_empty_results(self):
        self.assertEqual(
            validate_results({}),
            {},
        )

    def test_invalid_results_type(self):
        with self.assertRaises(ValueError):
            validate_results([])

    def test_missing_success(self):
        with self.assertRaises(ValueError):
            validate_results({
                "network": {
                    "host": "example.com"
                }
            })

    def test_invalid_success_type(self):
        with self.assertRaises(ValueError):
            validate_results({
                "network": {
                    "success": "yes"
                }
            })

    def test_invalid_module_name(self):
        with self.assertRaises(ValueError):
            validate_results({
                "": {
                    "success": True
                }
            })

    def test_invalid_module_result(self):
        with self.assertRaises(ValueError):
            validate_results({
                "network": "success"
            })


# ==========================================
# 3. Summary Tests
# ==========================================

class TestReportSummary(unittest.TestCase):

    def test_all_success(self):
        results = {
            "system": {"success": True},
            "network": {"success": True},
        }

        summary = generate_summary(results)

        self.assertEqual(
            summary["overall_status"],
            "HEALTHY",
        )

        self.assertEqual(
            summary["successful_checks"],
            2,
        )

    def test_all_failed(self):
        results = {
            "system": {"success": False},
            "network": {"success": False},
        }

        summary = generate_summary(results)

        self.assertEqual(
            summary["overall_status"],
            "UNHEALTHY",
        )

    def test_partial_failure(self):
        results = {
            "system": {"success": True},
            "network": {"success": False},
        }

        summary = generate_summary(results)

        self.assertEqual(
            summary["overall_status"],
            "DEGRADED",
        )

    def test_no_results(self):
        summary = generate_summary({})

        self.assertEqual(
            summary["overall_status"],
            "UNKNOWN",
        )

    def test_success_percentage(self):
        results = {
            "a": {"success": True},
            "b": {"success": True},
            "c": {"success": False},
        }

        summary = generate_summary(results)

        self.assertEqual(
            summary["success_percentage"],
            66.67,
        )

    def test_failed_modules(self):
        results = {
            "system": {"success": True},
            "network": {"success": False},
        }

        summary = generate_summary(results)

        self.assertEqual(
            summary["failed_modules"],
            ["network"],
        )


# ==========================================
# 4. Report Generation Tests
# ==========================================

class TestReportGeneration(unittest.TestCase):

    def test_generate_report(self):
        report = generate_report({
            "system": {"success": True}
        })

        self.assertIn(
            "report_id",
            report,
        )

        self.assertIn(
            "summary",
            report,
        )

        self.assertIn(
            "results",
            report,
        )

    def test_custom_application(self):
        report = generate_report(
            {},
            application="My DevOps App",
        )

        self.assertEqual(
            report["application"],
            "My DevOps App",
        )

    def test_invalid_application(self):
        with self.assertRaises(ValueError):
            generate_report(
                {},
                application="",
            )

    def test_invalid_environment(self):
        with self.assertRaises(ValueError):
            generate_report(
                {},
                environment="unknown",
            )

    def test_validate_generated_report(self):
        report = generate_report(
            {"system": {"success": True}}
        )

        validated = validate_report(report)

        self.assertEqual(
            validated["summary"]["overall_status"],
            "HEALTHY",
        )

    def test_missing_report_field(self):
        report = generate_report({})

        del report["report_id"]

        with self.assertRaises(ValueError):
            validate_report(report)

    def test_incorrect_summary(self):
        report = generate_report({
            "network": {"success": False}
        })

        report["summary"]["failed_checks"] = 0

        with self.assertRaises(ValueError):
            validate_report(report)


# ==========================================
# 5. Directory Tests
# ==========================================

class TestReportDirectory(unittest.TestCase):

    def test_create_directory(self):
        with tempfile.TemporaryDirectory() as directory:

            path = (
                Path(directory)
                / "reports"
            )

            result = ensure_report_directory(path)

            self.assertTrue(
                result.is_dir()
            )

    def test_existing_directory(self):
        with tempfile.TemporaryDirectory() as directory:

            result = ensure_report_directory(directory)

            self.assertTrue(
                result.is_dir()
            )

    def test_invalid_directory(self):
        with self.assertRaises(ValueError):
            ensure_report_directory("")


# ==========================================
# 6. Save and Load Tests
# ==========================================

class TestReportFiles(unittest.TestCase):

    def test_save_report(self):
        with tempfile.TemporaryDirectory() as directory:

            report = generate_report({
                "system": {"success": True}
            })

            path = save_report(
                report,
                output_directory=directory,
            )

            self.assertTrue(
                path.exists()
            )

    def test_saved_file_is_valid_json(self):
        with tempfile.TemporaryDirectory() as directory:

            report = generate_report({
                "system": {"success": True}
            })

            path = save_report(
                report,
                output_directory=directory,
            )

            with path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            self.assertEqual(
                data["report_id"],
                report["report_id"],
            )

    def test_load_report(self):
        with tempfile.TemporaryDirectory() as directory:

            report = generate_report({
                "network": {"success": True}
            })

            path = save_report(
                report,
                output_directory=directory,
            )

            loaded = load_report(path)

            self.assertEqual(
                loaded["report_id"],
                report["report_id"],
            )

    def test_duplicate_report(self):
        with tempfile.TemporaryDirectory() as directory:

            report = generate_report({})

            save_report(
                report,
                output_directory=directory,
            )

            with self.assertRaises(FileExistsError):
                save_report(
                    report,
                    output_directory=directory,
                )

    def test_unsupported_format(self):
        report = generate_report({})

        with self.assertRaises(ValueError):
            save_report(
                report,
                report_format="xml",
            )

    def test_missing_report_file(self):
        with tempfile.TemporaryDirectory() as directory:

            path = Path(directory) / "missing.json"

            with self.assertRaises(FileNotFoundError):
                load_report(path)

    def test_invalid_report_json(self):
        with tempfile.TemporaryDirectory() as directory:

            path = Path(directory) / "invalid.json"

            path.write_text(
                '{"invalid": }',
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_report(path)

    def test_invalid_report_id(self):
        with tempfile.TemporaryDirectory() as directory:

            report = generate_report({})

            report["report_id"] = "../invalid"

            with self.assertRaises(ValueError):
                save_report(
                    report,
                    output_directory=directory,
                )


# ==========================================
# 7. Configuration Integration Tests
# ==========================================

class TestConfiguredReports(unittest.TestCase):

    def test_generate_configured_report(self):
        results = get_sample_results()

        report = generate_configured_report(
            results,
            DEFAULT_CONFIG,
        )

        self.assertEqual(
            report["application"],
            DEFAULT_CONFIG["application"]["name"],
        )

    def test_save_configured_report(self):
        with tempfile.TemporaryDirectory() as directory:

            config = {
                **DEFAULT_CONFIG,
                "reporting": {
                    "output_directory": directory,
                    "format": "json",
                },
            }

            report = generate_configured_report(
                get_sample_results(),
                config,
            )

            path = save_configured_report(
                report,
                config,
            )

            self.assertTrue(
                path.exists()
            )


if __name__ == "__main__":
    unittest.main()