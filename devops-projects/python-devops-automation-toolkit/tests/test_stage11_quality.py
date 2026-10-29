"""
Stage 11 - Quality and Subprocess Tests

Tests:
- Python CLI startup
- Help output
- Invalid commands
- Invalid logging levels
- Python syntax compilation
"""

import subprocess
import sys
import unittest

from pathlib import Path


PROJECT_ROOT = (
    Path(__file__).resolve().parent.parent
)


class TestStage11Quality(unittest.TestCase):

    def run_process(self, *arguments):
        """
        Execute the CLI in a subprocess.
        """

        return subprocess.run(
            [
                sys.executable,
                "main.py",
                *arguments,
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )

    def test_help_command(self):

        result = self.run_process(
            "--help"
        )

        self.assertEqual(
            result.returncode,
            0,
        )

        self.assertIn(
            "Python DevOps Automation Toolkit",
            result.stdout,
        )

    def test_invalid_command(self):

        result = self.run_process(
            "invalid-command"
        )

        self.assertEqual(
            result.returncode,
            2,
        )

    def test_missing_command(self):

        result = self.run_process()

        self.assertEqual(
            result.returncode,
            2,
        )

    def test_invalid_logging_level(self):

        result = self.run_process(
            "--log-level",
            "INVALID",
            "all",
        )

        self.assertEqual(
            result.returncode,
            2,
        )

    def test_main_python_syntax(self):

        source = (
            PROJECT_ROOT / "main.py"
        ).read_text(
            encoding="utf-8"
        )

        compile(
            source,
            "main.py",
            "exec",
        )

    def test_logging_manager_syntax(self):

        path = (
            PROJECT_ROOT
            / "modules"
            / "logging_manager.py"
        )

        source = path.read_text(
            encoding="utf-8"
        )

        compile(
            source,
            str(path),
            "exec",
        )


if __name__ == "__main__":
    unittest.main()