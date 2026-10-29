"""
Stage 11 - CLI Integration Tests

Tests:
- CLI argument parsing
- Individual commands
- Combined monitoring
- Exit codes
- Report generation
- Report saving
- Configuration errors
- Logging errors
- JSON output
"""

import io
import json
import unittest

from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

import main


class TestStage11CLI(unittest.TestCase):

    def setUp(self):

        self.config = {
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
                "commands": ["whoami"],
                "timeout": 5,
            },
            "reporting": {
                "output_directory": "reports",
                "format": "json",
            },
        }

        # Mock configuration loading and logging.
        # No real log files are created.

        self.config_patcher = patch.object(
            main,
            "load_config",
            return_value=self.config,
        )

        self.paths_patcher = patch.object(
            main,
            "prepare_config_paths",
            side_effect=lambda config, path: config,
        )

        self.logging_patcher = patch.object(
            main,
            "setup_logging",
        )

        self.config_patcher.start()
        self.paths_patcher.start()
        self.logging_patcher.start()

        self.addCleanup(
            self.config_patcher.stop
        )

        self.addCleanup(
            self.paths_patcher.stop
        )

        self.addCleanup(
            self.logging_patcher.stop
        )

    def run_cli(self, arguments):
        """
        Run main() and capture stdout/stderr.
        """

        stdout = io.StringIO()
        stderr = io.StringIO()

        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                exit_code = main.main(
                    arguments
                )

        return (
            exit_code,
            stdout.getvalue(),
            stderr.getvalue(),
        )

    # ======================================
    # 1. Successful Command
    # ======================================

    @patch.object(main, "execute_module")
    def test_successful_network_command(
        self,
        mock_execute,
    ):

        mock_execute.return_value = {
            "success": True,
            "module": "network_checker",
        }

        code, output, _ = self.run_cli(
            ["network"]
        )

        self.assertEqual(
            code,
            0,
        )

        data = json.loads(output)

        self.assertTrue(
            data["success"]
        )

    # ======================================
    # 2. Failed Command
    # ======================================

    @patch.object(main, "execute_module")
    def test_failed_network_command(
        self,
        mock_execute,
    ):

        mock_execute.return_value = {
            "success": False,
            "module": "network_checker",
        }

        code, output, _ = self.run_cli(
            ["network"]
        )

        self.assertEqual(
            code,
            1,
        )

        self.assertFalse(
            json.loads(output)["success"]
        )

    # ======================================
    # 3. Disabled Module
    # ======================================

    @patch.object(main, "execute_module")
    def test_disabled_module(
        self,
        mock_execute,
    ):

        mock_execute.return_value = {
            "success": None,
            "module": "network_checker",
            "status": "SKIPPED",
        }

        code, output, _ = self.run_cli(
            ["network"]
        )

        self.assertEqual(
            code,
            0,
        )

        self.assertEqual(
            json.loads(output)["status"],
            "SKIPPED",
        )

    # ======================================
    # 4. Successful Combined Monitoring
    # ======================================

    @patch.object(main, "generate_configured_report")
    @patch.object(main, "execute_all")
    def test_all_success(
        self,
        mock_execute,
        mock_report,
    ):

        mock_execute.return_value = {
            "network_checker": {
                "success": True
            }
        }

        mock_report.return_value = {
            "summary": {
                "failed_checks": 0
            }
        }

        code, output, _ = self.run_cli(
            ["all"]
        )

        self.assertEqual(
            code,
            0,
        )

        self.assertIn(
            "HEALTHY",
            output,
        )

    # ======================================
    # 5. Failed Combined Monitoring
    # ======================================

    @patch.object(main, "generate_configured_report")
    @patch.object(main, "execute_all")
    def test_all_failure(
        self,
        mock_execute,
        mock_report,
    ):

        mock_execute.return_value = {
            "network_checker": {
                "success": False
            }
        }

        mock_report.return_value = {
            "summary": {
                "failed_checks": 1
            }
        }

        code, output, _ = self.run_cli(
            ["all"]
        )

        self.assertEqual(
            code,
            1,
        )

        self.assertIn(
            "UNHEALTHY",
            output,
        )

    # ======================================
    # 6. JSON Output
    # ======================================

    @patch.object(main, "generate_configured_report")
    @patch.object(main, "execute_all")
    def test_json_output(
        self,
        mock_execute,
        mock_report,
    ):

        mock_execute.return_value = {}

        mock_report.return_value = {
            "summary": {
                "failed_checks": 0
            },
            "results": {},
        }

        code, output, _ = self.run_cli(
            ["all", "--json"]
        )

        data = json.loads(
            output
        )

        self.assertEqual(
            code,
            0,
        )

        self.assertEqual(
            data["summary"]["failed_checks"],
            0,
        )

    # ======================================
    # 7. Report Saving
    # ======================================

    @patch.object(main, "save_configured_report")
    @patch.object(main, "generate_configured_report")
    @patch.object(main, "execute_all")
    def test_report_saved(
        self,
        mock_execute,
        mock_report,
        mock_save,
    ):

        mock_execute.return_value = {}

        mock_report.return_value = {
            "summary": {
                "failed_checks": 0
            }
        }

        mock_save.return_value = (
            "reports/test-report.json"
        )

        code, output, _ = self.run_cli(
            ["report"]
        )

        self.assertEqual(
            code,
            0,
        )

        mock_save.assert_called_once()

        self.assertIn(
            "Report saved to:",
            output,
        )

    # ======================================
    # 8. Report Save Failure
    # ======================================

    @patch.object(main, "save_configured_report")
    @patch.object(main, "generate_configured_report")
    @patch.object(main, "execute_all")
    def test_report_save_failure(
        self,
        mock_execute,
        mock_report,
        mock_save,
    ):

        mock_execute.return_value = {}

        mock_report.return_value = {
            "summary": {
                "failed_checks": 0
            }
        }

        mock_save.side_effect = OSError(
            "Simulated write failure"
        )

        code, _, error = self.run_cli(
            ["report"]
        )

        self.assertEqual(
            code,
            1,
        )

        self.assertIn(
            "Report saving failed",
            error,
        )

    # ======================================
    # 9. Configuration Failure
    # ======================================

    def test_configuration_failure(self):

        with patch.object(
            main,
            "load_config",
            side_effect=FileNotFoundError(
                "Configuration unavailable"
            ),
        ):

            code, _, error = self.run_cli(
                ["system"]
            )

        self.assertEqual(
            code,
            1,
        )

        self.assertIn(
            "Configuration error",
            error,
        )

    # ======================================
    # 10. Logging Failure
    # ======================================

    def test_logging_failure(self):

        with patch.object(
            main,
            "setup_logging",
            side_effect=OSError(
                "Permission denied"
            ),
        ):

            code, _, error = self.run_cli(
                ["system"]
            )

        self.assertEqual(
            code,
            1,
        )

        self.assertIn(
            "Logging initialization failed",
            error,
        )

    # ======================================
    # 11. Invalid Logging Level
    # ======================================

    def test_invalid_logging_level(self):

        parser = main.build_parser()

        with redirect_stderr(io.StringIO()):

            with self.assertRaises(
                SystemExit
            ) as context:

                parser.parse_args([
                    "--log-level",
                    "INVALID",
                    "all",
                ])

        self.assertEqual(
            context.exception.code,
            2,
        )

    # ======================================
    # 12. Custom Logging Level
    # ======================================

    def test_debug_logging_argument(self):

        parser = main.build_parser()

        args = parser.parse_args([
            "--log-level",
            "DEBUG",
            "all",
        ])

        self.assertEqual(
            args.log_level,
            "DEBUG",
        )

    # ======================================
    # 13. Console Logging Disabled
    # ======================================

    def test_disable_console_logging(self):

        parser = main.build_parser()

        args = parser.parse_args([
            "--no-console-log",
            "all",
        ])

        self.assertTrue(
            args.no_console_log
        )

    # ======================================
    # 14. Save Flag
    # ======================================

    def test_save_flag(self):

        parser = main.build_parser()

        args = parser.parse_args([
            "all",
            "--save",
        ])

        self.assertTrue(
            args.save
        )


if __name__ == "__main__":
    unittest.main()