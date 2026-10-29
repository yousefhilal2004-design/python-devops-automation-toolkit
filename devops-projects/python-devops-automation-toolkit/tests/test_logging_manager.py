"""
Stage 10 - Logging Manager Tests
"""

import logging
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from modules.logging_manager import (
    LOGGER_NAME,
    setup_logging,
    get_logger,
    log_module_start,
    log_module_result,
    log_module_exception,
    validate_logging_settings,
)


class TestLoggingManager(unittest.TestCase):

    def setUp(self):
        """
        Create an isolated temporary directory.
        """

        self.temp_directory = tempfile.TemporaryDirectory()

        self.addCleanup(
            self.temp_directory.cleanup
        )

        self.log_file = (
            Path(self.temp_directory.name)
            / "logs"
            / "test.log"
        )

        self.logger = logging.getLogger(
            LOGGER_NAME
        )

        # Preserve the original logger configuration.
        self.original_handlers = self.logger.handlers[:]
        self.original_level = self.logger.level
        self.original_propagate = self.logger.propagate

        # Detach original handlers without closing
        # them so they can be restored after the test.
        for handler in self.original_handlers:
            self.logger.removeHandler(handler)

        self.addCleanup(
            self.restore_logger
        )

    def restore_logger(self):
        """
        Close test handlers and restore logger state.
        """

        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            handler.close()

        for handler in self.original_handlers:
            self.logger.addHandler(handler)

        self.logger.setLevel(
            self.original_level
        )

        self.logger.propagate = (
            self.original_propagate
        )

    def configure(self, **kwargs):
        """
        Configure logging for an individual test.
        """

        return setup_logging(
            log_file=self.log_file,
            console=False,
            **kwargs,
        )

    def read_log(self):
        """
        Read the test log file.
        """

        return self.log_file.read_text(
            encoding="utf-8"
        )

    # --------------------------------------
    # Test 1
    # --------------------------------------

    def test_log_file_created(self):

        self.configure()

        self.assertTrue(
            self.log_file.exists()
        )

    # --------------------------------------
    # Test 2
    # --------------------------------------

    def test_info_message_written(self):

        logger = self.configure()

        logger.info(
            "Test application started"
        )

        self.assertIn(
            "Test application started",
            self.read_log(),
        )

    # --------------------------------------
    # Test 3
    # --------------------------------------

    def test_debug_filtered_at_info_level(self):

        logger = self.configure(
            level="INFO"
        )

        logger.debug(
            "Hidden debug message"
        )

        logger.info(
            "Visible info message"
        )

        content = self.read_log()

        self.assertNotIn(
            "Hidden debug message",
            content,
        )

        self.assertIn(
            "Visible info message",
            content,
        )

    # --------------------------------------
    # Test 4
    # --------------------------------------

    def test_debug_enabled(self):

        logger = self.configure(
            level="DEBUG"
        )

        logger.debug(
            "Debug information"
        )

        self.assertIn(
            "Debug information",
            self.read_log(),
        )

    # --------------------------------------
    # Test 5
    # --------------------------------------

    def test_invalid_level(self):

        with self.assertRaises(ValueError):
            self.configure(
                level="INVALID"
            )

    # --------------------------------------
    # Test 6
    # --------------------------------------

    def test_invalid_max_bytes(self):

        with self.assertRaises(ValueError):
            self.configure(
                max_bytes=0
            )

    # --------------------------------------
    # Test 7
    # --------------------------------------

    def test_invalid_backup_count(self):

        with self.assertRaises(ValueError):
            self.configure(
                backup_count=-1
            )

    # --------------------------------------
    # Test 8
    # --------------------------------------

    def test_invalid_boolean_max_bytes(self):

        with self.assertRaises(ValueError):
            self.configure(
                max_bytes=True
            )

    # --------------------------------------
    # Test 9
    # --------------------------------------

    def test_duplicate_handlers_prevented(self):

        self.configure()

        self.configure()

        self.assertEqual(
            len(self.logger.handlers),
            1,
        )

    # --------------------------------------
    # Test 10
    # --------------------------------------

    def test_console_handler_uses_stderr(self):

        with patch(
            "modules.logging_manager.sys.stderr"
        ) as mock_stderr:

            setup_logging(
                log_file=self.log_file,
                console=True,
            )

            self.logger.info(
                "Console test"
            )

            self.assertTrue(
                mock_stderr.write.called
            )

    # --------------------------------------
    # Test 11
    # --------------------------------------

    def test_get_logger(self):

        logger = get_logger()

        self.assertEqual(
            logger.name,
            LOGGER_NAME,
        )

    # --------------------------------------
    # Test 12
    # --------------------------------------

    def test_child_logger(self):

        logger = get_logger(
            "network"
        )

        self.assertEqual(
            logger.name,
            f"{LOGGER_NAME}.network",
        )

    # --------------------------------------
    # Test 13
    # --------------------------------------

    def test_log_module_start(self):

        logger = self.configure()

        log_module_start(
            logger,
            "system_monitor",
        )

        self.assertIn(
            "Starting module: system_monitor",
            self.read_log(),
        )

    # --------------------------------------
    # Test 14
    # --------------------------------------

    def test_log_module_success(self):

        logger = self.configure()

        log_module_result(
            logger,
            "network_checker",
            True,
            25.5,
        )

        content = self.read_log()

        self.assertIn(
            "network_checker completed: PASS",
            content,
        )

        self.assertIn(
            "25.50 ms",
            content,
        )

    # --------------------------------------
    # Test 15
    # --------------------------------------

    def test_log_module_failure(self):

        logger = self.configure()

        log_module_result(
            logger,
            "website_checker",
            False,
            120.0,
        )

        self.assertIn(
            "website_checker completed: FAIL",
            self.read_log(),
        )

    # --------------------------------------
    # Test 16
    # --------------------------------------

    def test_exception_type_logged(self):

        logger = self.configure()

        error = ValueError(
            "Sensitive example message"
        )

        log_module_exception(
            logger,
            "network_checker",
            error,
        )

        content = self.read_log()

        self.assertIn(
            "ValueError",
            content,
        )

        self.assertNotIn(
            "Sensitive example message",
            content,
        )

    # --------------------------------------
    # Test 17
    # --------------------------------------

    def test_log_rotation(self):

        logger = self.configure(
            max_bytes=200,
            backup_count=2,
        )

        for number in range(50):
            logger.info(
                "Rotation test message number %d",
                number,
            )

        rotated_file = Path(
            str(self.log_file) + ".1"
        )

        self.assertTrue(
            rotated_file.exists()
        )

    # --------------------------------------
    # Test 18
    # --------------------------------------

    def test_validate_settings(self):

        level = validate_logging_settings(
            "debug",
            1000,
            3,
        )

        self.assertEqual(
            level,
            "DEBUG",
        )


if __name__ == "__main__":
    unittest.main()