"""
Stage 11 - Module Integration Tests

Tests:
- System monitor
- Network checker
- Website checker
- Log analyzer
- Command runner
- Module dispatch
- Disabled modules
- Error handling
"""

import unittest

from unittest.mock import patch

import main


class TestStage11Modules(unittest.TestCase):

    def setUp(self):
        """
        Create a minimal configuration
        for module integration tests.
        """

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
        }

    # ======================================
    # 1. System Monitor
    # ======================================

    @patch.object(main, "check_thresholds")
    @patch.object(main, "get_system_info")
    def test_system_monitor_success(
        self,
        mock_info,
        mock_thresholds,
    ):

        mock_info.return_value = {
            "cpu_percent": 20,
            "memory": {"percent": 40},
            "disk": {"percent": 50},
        }

        mock_thresholds.return_value = [
            "System resource usage is below warning thresholds"
        ]

        result = main.run_system(
            self.config
        )

        self.assertTrue(
            result["success"]
        )

        mock_thresholds.assert_called_once_with(
            mock_info.return_value,
            cpu_threshold=80,
            memory_threshold=85,
            disk_threshold=90,
        )

    @patch.object(main, "check_thresholds")
    @patch.object(main, "get_system_info")
    def test_system_monitor_warning(
        self,
        mock_info,
        mock_thresholds,
    ):

        mock_info.return_value = {
            "cpu_percent": 95,
            "memory": {"percent": 40},
            "disk": {"percent": 50},
        }

        mock_thresholds.return_value = [
            "WARNING: High CPU usage"
        ]

        result = main.run_system(
            self.config
        )

        self.assertFalse(
            result["success"]
        )

    # ======================================
    # 2. Network Checker
    # ======================================

    @patch.object(main, "run_network_diagnostic")
    def test_network_success(
        self,
        mock_network,
    ):

        mock_network.return_value = {
            "overall_status": "PASS",
            "tcp": {"success": True},
        }

        result = main.run_network(
            self.config
        )

        self.assertTrue(
            result["success"]
        )

    @patch.object(main, "run_network_diagnostic")
    def test_network_failure(
        self,
        mock_network,
    ):

        mock_network.return_value = {
            "overall_status": "FAIL",
            "tcp": {"success": False},
        }

        result = main.run_network(
            self.config
        )

        self.assertFalse(
            result["success"]
        )

    # ======================================
    # 3. Website Checker
    # ======================================

    @patch.object(main, "check_website")
    def test_website_healthy(
        self,
        mock_website,
    ):

        mock_website.return_value = {
            "healthy": True,
            "status_code": 200,
        }

        result = main.run_website(
            self.config
        )

        self.assertTrue(
            result["success"]
        )

    @patch.object(main, "check_website")
    def test_website_unhealthy(
        self,
        mock_website,
    ):

        mock_website.return_value = {
            "healthy": False,
            "status_code": 503,
        }

        result = main.run_website(
            self.config
        )

        self.assertFalse(
            result["success"]
        )

    # ======================================
    # 4. Log Analyzer
    # ======================================

    @patch.object(main, "analyze_log_file")
    def test_log_analyzer_success(
        self,
        mock_analyzer,
    ):

        mock_analyzer.return_value = {
            "summary": {
                "total_lines": 100,
                "error_count": 3,
            }
        }

        result = main.run_logs(
            self.config
        )

        self.assertTrue(
            result["success"]
        )

        self.assertEqual(
            result["data"]["summary"]["error_count"],
            3,
        )

    @patch.object(main, "analyze_log_file")
    def test_log_analyzer_error(
        self,
        mock_analyzer,
    ):

        mock_analyzer.return_value = {
            "error": "Log file unavailable"
        }

        result = main.run_logs(
            self.config
        )

        self.assertFalse(
            result["success"]
        )

    # ======================================
    # 5. Command Runner
    # ======================================

    @patch.object(main, "run_command")
    def test_command_runner_success(
        self,
        mock_command,
    ):

        mock_command.return_value = {
            "success": True,
            "return_code": 0,
            "stdout": "yousef",
        }

        result = main.run_commands(
            self.config
        )

        self.assertTrue(
            result["success"]
        )

        self.assertEqual(
            result["successful_commands"],
            1,
        )

    @patch.object(main, "run_command")
    def test_command_runner_failure(
        self,
        mock_command,
    ):

        mock_command.return_value = {
            "success": False,
            "return_code": 1,
            "stderr": "Command failed",
        }

        result = main.run_commands(
            self.config
        )

        self.assertFalse(
            result["success"]
        )

        self.assertEqual(
            result["failed_commands"],
            1,
        )

    # ======================================
    # 6. Module Dispatch
    # ======================================

    @patch.object(main, "run_network")
    def test_execute_module_success(
        self,
        mock_runner,
    ):

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
    def test_execute_module_exception(
        self,
        mock_runner,
    ):

        mock_runner.side_effect = RuntimeError(
            "Simulated network error"
        )

        result = main.execute_module(
            "network_checker",
            self.config,
        )

        self.assertFalse(
            result["success"]
        )

        self.assertIn(
            "error",
            result,
        )

    # ======================================
    # 7. Disabled Module
    # ======================================

    @patch.object(main, "run_network")
    def test_disabled_module(
        self,
        mock_runner,
    ):

        self.config["network_checker"]["enabled"] = False

        result = main.execute_module(
            "network_checker",
            self.config,
        )

        self.assertEqual(
            result["status"],
            "SKIPPED",
        )

        mock_runner.assert_not_called()

    # ======================================
    # 8. Invalid Result
    # ======================================

    @patch.object(main, "run_network")
    def test_invalid_module_result(
        self,
        mock_runner,
    ):

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

    # ======================================
    # 9. Unknown Module
    # ======================================

    def test_unknown_module(self):

        with self.assertRaises(ValueError):
            main.execute_module(
                "unknown_module",
                self.config,
            )


if __name__ == "__main__":
    unittest.main()