"""
Automated tests for Safe Linux Command Runner.
"""

import subprocess
import unittest

from unittest.mock import patch

from modules.command_runner import (
    ALLOWED_COMMANDS,
    run_all_commands,
    run_command,
    validate_command,
    validate_timeout,
)


# ==========================================
# 1. Command Validation Tests
# ==========================================

class TestCommandValidation(unittest.TestCase):

    def test_valid_command(self):
        self.assertEqual(
            validate_command("uptime"),
            "uptime",
        )

    def test_valid_command_with_spaces(self):
        self.assertEqual(
            validate_command(" uptime "),
            "uptime",
        )

    def test_invalid_command(self):
        with self.assertRaises(ValueError):
            validate_command("unknown")

    def test_empty_command(self):
        with self.assertRaises(ValueError):
            validate_command("")

    def test_non_string_command(self):
        with self.assertRaises(ValueError):
            validate_command(123)


# ==========================================
# 2. Timeout Validation Tests
# ==========================================

class TestTimeoutValidation(unittest.TestCase):

    def test_valid_timeout(self):
        self.assertEqual(
            validate_timeout(5),
            5.0,
        )

    def test_zero_timeout(self):
        with self.assertRaises(ValueError):
            validate_timeout(0)

    def test_negative_timeout(self):
        with self.assertRaises(ValueError):
            validate_timeout(-1)

    def test_large_timeout(self):
        with self.assertRaises(ValueError):
            validate_timeout(100)

    def test_invalid_timeout(self):
        with self.assertRaises(ValueError):
            validate_timeout("invalid")


# ==========================================
# 3. Command Execution Tests
# ==========================================

class TestCommandRunner(unittest.TestCase):

    @patch("modules.command_runner.subprocess.run")
    def test_successful_command(self, mock_run):

        mock_run.return_value = subprocess.CompletedProcess(
            args=["whoami"],
            returncode=0,
            stdout="yousef\n",
            stderr="",
        )

        result = run_command("whoami")

        self.assertTrue(result["success"])
        self.assertEqual(result["return_code"], 0)
        self.assertEqual(result["stdout"], "yousef")
        self.assertIsNone(result["error"])

        mock_run.assert_called_once_with(
            ["whoami"],
            capture_output=True,
            text=True,
            timeout=5.0,
            shell=False,
            check=False,
        )

    @patch("modules.command_runner.subprocess.run")
    def test_failed_command(self, mock_run):

        mock_run.return_value = subprocess.CompletedProcess(
            args=["uptime"],
            returncode=1,
            stdout="",
            stderr="Command failed",
        )

        result = run_command("uptime")

        self.assertFalse(result["success"])
        self.assertEqual(result["return_code"], 1)
        self.assertEqual(
            result["error"],
            "Command returned a nonzero exit code",
        )

    @patch("modules.command_runner.subprocess.run")
    def test_command_timeout(self, mock_run):

        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=["uptime"],
            timeout=5,
        )

        result = run_command("uptime")

        self.assertFalse(result["success"])
        self.assertEqual(
            result["error"],
            "Command execution timed out",
        )

    @patch("modules.command_runner.subprocess.run")
    def test_command_not_found(self, mock_run):

        mock_run.side_effect = FileNotFoundError()

        result = run_command("uptime")

        self.assertFalse(result["success"])
        self.assertEqual(
            result["error"],
            "Required Linux command was not found",
        )

    @patch("modules.command_runner.subprocess.run")
    def test_permission_error(self, mock_run):

        mock_run.side_effect = PermissionError()

        result = run_command("uptime")

        self.assertFalse(result["success"])
        self.assertEqual(
            result["error"],
            "Permission denied while executing command",
        )

    @patch("modules.command_runner.subprocess.run")
    def test_os_error(self, mock_run):

        mock_run.side_effect = OSError()

        result = run_command("uptime")

        self.assertFalse(result["success"])
        self.assertEqual(
            result["error"],
            "Operating system error while executing command",
        )

    @patch("modules.command_runner.subprocess.run")
    def test_disk_command_arguments(self, mock_run):

        mock_run.return_value = subprocess.CompletedProcess(
            args=["df", "-h", "/"],
            returncode=0,
            stdout="Disk information",
            stderr="",
        )

        result = run_command("disk")

        self.assertTrue(result["success"])
        self.assertEqual(
            result["arguments"],
            ["df", "-h", "/"],
        )

    @patch("modules.command_runner.subprocess.run")
    def test_execution_time(self, mock_run):

        mock_run.return_value = subprocess.CompletedProcess(
            args=["uptime"],
            returncode=0,
            stdout="System uptime",
            stderr="",
        )

        result = run_command("uptime")

        self.assertIsNotNone(
            result["execution_time_ms"]
        )

        self.assertGreaterEqual(
            result["execution_time_ms"],
            0,
        )


# ==========================================
# 4. Run All Commands Tests
# ==========================================

class TestRunAllCommands(unittest.TestCase):

    @patch("modules.command_runner.run_command")
    def test_all_commands_success(self, mock_command):

        mock_command.return_value = {
            "success": True,
        }

        result = run_all_commands()

        self.assertEqual(
            result["total_commands"],
            len(ALLOWED_COMMANDS),
        )

        self.assertEqual(
            result["successful_commands"],
            len(ALLOWED_COMMANDS),
        )

        self.assertEqual(
            result["failed_commands"],
            0,
        )

        self.assertEqual(
            result["overall_status"],
            "PASS",
        )

    @patch("modules.command_runner.run_command")
    def test_all_commands_failure(self, mock_command):

        mock_command.return_value = {
            "success": False,
        }

        result = run_all_commands()

        self.assertEqual(
            result["successful_commands"],
            0,
        )

        self.assertEqual(
            result["failed_commands"],
            len(ALLOWED_COMMANDS),
        )

        self.assertEqual(
            result["overall_status"],
            "FAIL",
        )


if __name__ == "__main__":
    unittest.main()