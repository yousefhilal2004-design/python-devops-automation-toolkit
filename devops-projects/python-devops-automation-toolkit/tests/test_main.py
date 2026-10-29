"""
Stage 9 - Main CLI Integration Tests

Python DevOps Automation Toolkit
"""

import io
import unittest

from copy import deepcopy
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

import main

from modules.config_manager import DEFAULT_CONFIG


# ==========================================
# 1. Error Result Tests
# ==========================================

class TestErrorResult(unittest.TestCase):

    def test_error_result_structure(self):

        result = main.error_result(
            "network_checker",
            ValueError("Connection failed"),
        )

        self.assertFalse(result["success"])

        self.assertEqual(
            result["module"],
            "network_checker",
        )

        self.assertEqual(
            result["error"],
            "Connection failed",
        )


# ==========================================
# 2. Module Execution Tests
# ==========================================

class TestModuleExecution(unittest.TestCase):

    def setUp(self):
        self.config = deepcopy(DEFAULT_CONFIG)

    def test_unknown_module(self):

        with self.assertRaises(ValueError):

            main.execute_module(
                "unknown_module",
                self.config,
            )

    def test_disabled_module(self):

        self.config["network_checker"]["enabled"] = False

        result = main.execute_module(
            "network_checker",
            self.config,
        )

        self.assertEqual(
            result["status"],
            "SKIPPED",
        )

        self.assertIsNone(
            result["success"]
        )

    @patch.object(main, "run_network")
    def test_successful_module(self, mock_runner):

        mock_runner.return_value = {
            "success": True,
            "module": "network_checker",
        }

        result = main.execute_module(
            "network_checker",
            self.config,
        )

        self.assertTrue(
            result["success"]
        )

        mock_runner.assert_called_once_with(
            self.config
        )

    @patch.object(main, "run_network")
    def test_failed_module(self, mock_runner):

        mock_runner.return_value = {
            "success": False,
            "module": "network_checker",
        }

        result = main.execute_module(
            "network_checker",
            self.config,
        )

        self.assertFalse(
            result["success"]
        )

    @patch.object(main, "run_network")
    def test_module_exception(self, mock_runner):

        mock_runner.side_effect = ValueError(
            "Network error"
        )

        result = main.execute_module(
            "network_checker",
            self.config,
        )

        self.assertFalse(
            result["success"]
        )

        self.assertEqual(
            result["error"],
            "Network error",
        )

    @patch.object(main, "run_network")
    def test_invalid_module_result(self, mock_runner):

        mock_runner.return_value = {
            "module": "network_checker"
        }

        result = main.execute_module(
            "network_checker",
            self.config,
        )

        self.assertFalse(
            result["success"]
        )


# ==========================================
# 3. Combined Execution Tests
# ==========================================

class TestExecuteAll(unittest.TestCase):

    def setUp(self):
        self.config = deepcopy(DEFAULT_CONFIG)

    @patch.object(main, "execute_module")
    def test_all_modules_execute(self, mock_execute):

        mock_execute.side_effect = (
            lambda name, config: {
                "success": True,
                "module": name,
            }
        )

        results = main.execute_all(
            self.config
        )

        self.assertEqual(
            len(results),
            5,
        )

    @patch.object(main, "execute_module")
    def test_disabled_module_excluded(self, mock_execute):

        def fake_execute(name, config):

            if name == "network_checker":
                return {
                    "success": None,
                    "module": name,
                    "status": "SKIPPED",
                }

            return {
                "success": True,
                "module": name,
            }

        mock_execute.side_effect = fake_execute

        results = main.execute_all(
            self.config
        )

        self.assertNotIn(
            "network_checker",
            results,
        )

        self.assertEqual(
            len(results),
            4,
        )

    @patch.object(main, "execute_module")
    def test_failure_does_not_stop_other_modules(
        self,
        mock_execute,
    ):

        def fake_execute(name, config):

            return {
                "success": name != "website_checker",
                "module": name,
            }

        mock_execute.side_effect = fake_execute

        results = main.execute_all(
            self.config
        )

        self.assertEqual(
            len(results),
            5,
        )

        self.assertFalse(
            results["website_checker"]["success"]
        )

        self.assertTrue(
            results["network_checker"]["success"]
        )


# ==========================================
# 4. Output Tests
# ==========================================

class TestOutput(unittest.TestCase):

    def test_print_json(self):

        output = io.StringIO()

        with redirect_stdout(output):

            main.print_json({
                "success": True
            })

        self.assertIn(
            '"success": true',
            output.getvalue(),
        )

    def test_text_summary(self):

        results = {
            "system_monitor": {
                "success": True
            },
            "network_checker": {
                "success": False
            },
        }

        output = io.StringIO()

        with redirect_stdout(output):

            main.print_text_summary(
                results
            )

        text = output.getvalue()

        self.assertIn(
            "DEGRADED",
            text,
        )

        self.assertIn(
            "Successful:   1",
            text,
        )

        self.assertIn(
            "Failed:       1",
            text,
        )

    def test_empty_summary(self):

        output = io.StringIO()

        with redirect_stdout(output):

            main.print_text_summary({})

        self.assertIn(
            "UNKNOWN",
            output.getvalue(),
        )


# ==========================================
# 5. CLI Parser Tests
# ==========================================

class TestCLIParser(unittest.TestCase):

    def test_system_command(self):

        parser = main.build_parser()

        args = parser.parse_args([
            "system"
        ])

        self.assertEqual(
            args.command,
            "system",
        )

    def test_network_command(self):

        parser = main.build_parser()

        args = parser.parse_args([
            "network",
            "--json",
        ])

        self.assertEqual(
            args.command,
            "network",
        )

        self.assertTrue(
            args.json
        )

    def test_all_save_flag(self):

        parser = main.build_parser()

        args = parser.parse_args([
            "all",
            "--save",
        ])

        self.assertTrue(
            args.save
        )

    def test_custom_config(self):

        parser = main.build_parser()

        args = parser.parse_args([
            "--config",
            "custom.json",
            "system",
        ])

        self.assertEqual(
            args.config,
            "custom.json",
        )

    def test_missing_command(self):

        parser = main.build_parser()

        with self.assertRaises(SystemExit):

            with redirect_stderr(io.StringIO()):

                parser.parse_args([])


# ==========================================
# 6. Main Application Tests
# ==========================================

class TestMainApplication(unittest.TestCase):

    def setUp(self):
        self.config = deepcopy(DEFAULT_CONFIG)

    @patch.object(main, "load_config")
    @patch.object(main, "execute_module")
    def test_successful_system_command(
        self,
        mock_execute,
        mock_load,
    ):

        mock_load.return_value = deepcopy(
            self.config
        )

        mock_execute.return_value = {
            "success": True,
            "module": "system_monitor",
        }

        with redirect_stdout(io.StringIO()):

            result = main.main([
                "system"
            ])

        self.assertEqual(
            result,
            0,
        )

    @patch.object(main, "load_config")
    @patch.object(main, "execute_module")
    def test_failed_network_command(
        self,
        mock_execute,
        mock_load,
    ):

        mock_load.return_value = deepcopy(
            self.config
        )

        mock_execute.return_value = {
            "success": False,
            "module": "network_checker",
        }

        with redirect_stdout(io.StringIO()):

            result = main.main([
                "network"
            ])

        self.assertEqual(
            result,
            1,
        )

    @patch.object(main, "load_config")
    @patch.object(main, "execute_module")
    def test_disabled_module_exit_code(
        self,
        mock_execute,
        mock_load,
    ):

        mock_load.return_value = deepcopy(
            self.config
        )

        mock_execute.return_value = {
            "success": None,
            "module": "network_checker",
            "status": "SKIPPED",
        }

        with redirect_stdout(io.StringIO()):

            result = main.main([
                "network"
            ])

        self.assertEqual(
            result,
            0,
        )

    @patch.object(main, "load_config")
    def test_config_error(
        self,
        mock_load,
    ):

        mock_load.side_effect = FileNotFoundError(
            "Missing configuration"
        )

        with redirect_stderr(io.StringIO()):

            result = main.main([
                "system"
            ])

        self.assertEqual(
            result,
            1,
        )

    @patch.object(main, "load_config")
    @patch.object(main, "execute_all")
    def test_all_success(
        self,
        mock_all,
        mock_load,
    ):

        mock_load.return_value = deepcopy(
            self.config
        )

        mock_all.return_value = {
            "system_monitor": {
                "success": True
            },
            "network_checker": {
                "success": True
            },
        }

        with redirect_stdout(io.StringIO()):

            result = main.main([
                "all"
            ])

        self.assertEqual(
            result,
            0,
        )

    @patch.object(main, "load_config")
    @patch.object(main, "execute_all")
    def test_all_failure(
        self,
        mock_all,
        mock_load,
    ):

        mock_load.return_value = deepcopy(
            self.config
        )

        mock_all.return_value = {
            "system_monitor": {
                "success": True
            },
            "network_checker": {
                "success": False
            },
        }

        with redirect_stdout(io.StringIO()):

            result = main.main([
                "all"
            ])

        self.assertEqual(
            result,
            1,
        )

    @patch.object(main, "load_config")
    @patch.object(main, "execute_all")
    @patch.object(main, "save_configured_report")
    def test_report_saving(
        self,
        mock_save,
        mock_all,
        mock_load,
    ):

        mock_load.return_value = deepcopy(
            self.config
        )

        mock_all.return_value = {
            "system_monitor": {
                "success": True
            }
        }

        mock_save.return_value = (
            "reports/test_report.json"
        )

        with redirect_stdout(io.StringIO()):

            result = main.main([
                "report"
            ])

        self.assertEqual(
            result,
            0,
        )

        mock_save.assert_called_once()

    @patch.object(main, "load_config")
    @patch.object(main, "execute_all")
    @patch.object(main, "save_configured_report")
    def test_report_save_failure(
        self,
        mock_save,
        mock_all,
        mock_load,
    ):

        mock_load.return_value = deepcopy(
            self.config
        )

        mock_all.return_value = {
            "system_monitor": {
                "success": True
            }
        }

        mock_save.side_effect = OSError(
            "Permission denied"
        )

        with (
            redirect_stdout(io.StringIO()),
            redirect_stderr(io.StringIO()),
        ):

            result = main.main([
                "report"
            ])

        self.assertEqual(
            result,
            1,
        )


if __name__ == "__main__":
    unittest.main()