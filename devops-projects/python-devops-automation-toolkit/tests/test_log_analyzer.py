"""
Automated tests for the Log Analyzer module.
"""

import tempfile
import unittest

from pathlib import Path

from modules.log_analyzer import (
    analyze_log_file,
    calculate_percentage,
    parse_log_line,
    validate_log_file,
)


# ==========================================
# 1. Log Parsing Tests
# ==========================================

class TestLogParsing(unittest.TestCase):

    def test_valid_info_line(self):

        line = (
            "2026-10-29 10:00:00 "
            "INFO Application started"
        )

        result = parse_log_line(line)

        self.assertEqual(
            result["level"],
            "INFO",
        )

        self.assertEqual(
            result["message"],
            "Application started",
        )

    def test_valid_error_line(self):

        line = (
            "2026-10-29 10:01:00 "
            "ERROR Database connection failed"
        )

        result = parse_log_line(line)

        self.assertEqual(
            result["level"],
            "ERROR",
        )

    def test_invalid_line(self):

        result = parse_log_line(
            "This is not a valid log line"
        )

        self.assertIsNone(result)

    def test_invalid_timestamp(self):

        result = parse_log_line(
            "2026-99-99 10:00:00 "
            "INFO Invalid date"
        )

        self.assertIsNone(result)

    def test_unsupported_level(self):

        result = parse_log_line(
            "2026-10-29 10:00:00 "
            "TRACE Unsupported level"
        )

        self.assertIsNone(result)


# ==========================================
# 2. Percentage Tests
# ==========================================

class TestPercentage(unittest.TestCase):

    def test_normal_percentage(self):

        self.assertEqual(
            calculate_percentage(5, 20),
            25.0,
        )

    def test_zero_total(self):

        self.assertEqual(
            calculate_percentage(0, 0),
            0.0,
        )

    def test_full_percentage(self):

        self.assertEqual(
            calculate_percentage(10, 10),
            100.0,
        )


# ==========================================
# 3. File Validation Tests
# ==========================================

class TestFileValidation(unittest.TestCase):

    def test_missing_file(self):

        with tempfile.TemporaryDirectory() as directory:

            missing_path = (
                Path(directory) / "missing.log"
            )

            with self.assertRaises(FileNotFoundError):
                validate_log_file(missing_path)

    def test_directory_instead_of_file(self):

        with tempfile.TemporaryDirectory() as directory:

            with self.assertRaises(ValueError):
                validate_log_file(directory)


# ==========================================
# 4. Complete Analyzer Tests
# ==========================================

class TestLogAnalyzer(unittest.TestCase):

    def setUp(self):

        self.temp_directory = tempfile.TemporaryDirectory()

        self.log_path = (
            Path(self.temp_directory.name)
            / "application.log"
        )

        self.log_path.write_text(
            "\n".join([
                "2026-10-29 10:00:00 INFO Started",
                "2026-10-29 10:01:00 WARNING High CPU",
                "2026-10-29 10:02:00 ERROR Database failed",
                "2026-10-29 10:03:00 ERROR Database failed",
                "2026-10-29 10:04:00 CRITICAL Service down",
                "Invalid log entry",
            ]) + "\n",
            encoding="utf-8",
        )

    def tearDown(self):

        self.temp_directory.cleanup()

    def test_total_lines(self):

        result = analyze_log_file(self.log_path)

        self.assertEqual(
            result["summary"]["total_lines"],
            6,
        )

    def test_valid_lines(self):

        result = analyze_log_file(self.log_path)

        self.assertEqual(
            result["summary"]["valid_lines"],
            5,
        )

    def test_malformed_lines(self):

        result = analyze_log_file(self.log_path)

        self.assertEqual(
            result["summary"]["malformed_lines"],
            1,
        )

    def test_log_level_counts(self):

        result = analyze_log_file(self.log_path)

        counts = result["summary"]["log_levels"]

        self.assertEqual(counts["INFO"], 1)
        self.assertEqual(counts["WARNING"], 1)
        self.assertEqual(counts["ERROR"], 2)
        self.assertEqual(counts["CRITICAL"], 1)
        self.assertEqual(counts["DEBUG"], 0)

    def test_error_count(self):

        result = analyze_log_file(self.log_path)

        self.assertEqual(
            result["summary"]["error_count"],
            3,
        )

    def test_warning_count(self):

        result = analyze_log_file(self.log_path)

        self.assertEqual(
            result["summary"]["warning_count"],
            1,
        )

    def test_error_percentage(self):

        result = analyze_log_file(self.log_path)

        self.assertEqual(
            result["summary"]["error_percentage"],
            60.0,
        )

    def test_warning_percentage(self):

        result = analyze_log_file(self.log_path)

        self.assertEqual(
            result["summary"]["warning_percentage"],
            20.0,
        )

    def test_top_error(self):

        result = analyze_log_file(
            self.log_path,
            top_n=1,
        )

        self.assertEqual(
            len(result["top_errors"]),
            1,
        )

        self.assertEqual(
            result["top_errors"][0]["message"],
            "Database failed",
        )

        self.assertEqual(
            result["top_errors"][0]["count"],
            2,
        )

    def test_first_timestamp(self):

        result = analyze_log_file(self.log_path)

        self.assertEqual(
            result["summary"]["first_timestamp"],
            "2026-10-29 10:00:00",
        )

    def test_last_timestamp(self):

        result = analyze_log_file(self.log_path)

        self.assertEqual(
            result["summary"]["last_timestamp"],
            "2026-10-29 10:04:00",
        )

    def test_invalid_top_n(self):

        with self.assertRaises(ValueError):
            analyze_log_file(
                self.log_path,
                top_n=0,
            )

    def test_empty_file(self):

        self.log_path.write_text(
            "",
            encoding="utf-8",
        )

        result = analyze_log_file(self.log_path)

        self.assertEqual(
            result["summary"]["total_lines"],
            0,
        )

        self.assertEqual(
            result["summary"]["error_percentage"],
            0.0,
        )


if __name__ == "__main__":
    unittest.main()