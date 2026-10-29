import socket
import unittest
from unittest.mock import patch

from modules.network_checker import (
    check_tcp_connection,
    resolve_dns,
    run_network_diagnostic,
    validate_host,
    validate_port,
    validate_timeout,
)


class TestInputValidation(unittest.TestCase):

    def test_valid_host(self):
        self.assertEqual(
            validate_host(" example.com "),
            "example.com",
        )

    def test_empty_host(self):
        with self.assertRaises(ValueError):
            validate_host("")

    def test_host_with_spaces(self):
        with self.assertRaises(ValueError):
            validate_host("example .com")

    def test_valid_port(self):
        self.assertEqual(
            validate_port(443),
            443,
        )

    def test_invalid_port(self):
        with self.assertRaises(ValueError):
            validate_port(70000)

    def test_zero_port(self):
        with self.assertRaises(ValueError):
            validate_port(0)

    def test_valid_timeout(self):
        self.assertEqual(
            validate_timeout(3),
            3.0,
        )

    def test_invalid_timeout(self):
        with self.assertRaises(ValueError):
            validate_timeout(-1)


class TestDNSResolution(unittest.TestCase):

    @patch("modules.network_checker.socket.getaddrinfo")
    def test_dns_success(self, mock_getaddrinfo):

        mock_getaddrinfo.return_value = [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                ("192.0.2.10", 0),
            )
        ]

        result = resolve_dns("example.com")

        self.assertTrue(result["success"])
        self.assertEqual(
            result["ip_addresses"],
            ["192.0.2.10"],
        )

    @patch("modules.network_checker.socket.getaddrinfo")
    def test_dns_failure(self, mock_getaddrinfo):

        mock_getaddrinfo.side_effect = socket.gaierror(
            "Name resolution failed"
        )

        result = resolve_dns("example.invalid")

        self.assertFalse(result["success"])
        self.assertEqual(result["ip_addresses"], [])


class TestTCPConnection(unittest.TestCase):

    @patch("modules.network_checker.socket.create_connection")
    def test_tcp_success(self, mock_connection):

        result = check_tcp_connection(
            "example.com",
            443,
        )

        self.assertTrue(result["success"])
        self.assertIsNotNone(
            result["connection_time_ms"]
        )

        mock_connection.assert_called_once_with(
            ("example.com", 443),
            timeout=3.0,
        )

    @patch("modules.network_checker.socket.create_connection")
    def test_connection_refused(self, mock_connection):

        mock_connection.side_effect = ConnectionRefusedError()

        result = check_tcp_connection(
            "127.0.0.1",
            65000,
        )

        self.assertFalse(result["success"])
        self.assertEqual(
            result["error"],
            "Connection refused",
        )

    @patch("modules.network_checker.socket.create_connection")
    def test_connection_timeout(self, mock_connection):

        mock_connection.side_effect = socket.timeout()

        result = check_tcp_connection(
            "example.com",
            443,
        )

        self.assertFalse(result["success"])
        self.assertEqual(
            result["error"],
            "Connection timed out",
        )


class TestNetworkDiagnostic(unittest.TestCase):

    @patch("modules.network_checker.check_tcp_connection")
    @patch("modules.network_checker.resolve_dns")
    def test_overall_pass(
        self,
        mock_dns,
        mock_tcp,
    ):

        mock_dns.return_value = {
            "success": True,
            "ip_addresses": ["192.0.2.10"],
            "error": None,
        }

        mock_tcp.return_value = {
            "success": True,
            "connection_time_ms": 20.0,
            "error": None,
        }

        result = run_network_diagnostic(
            "example.com",
            443,
        )

        self.assertEqual(
            result["overall_status"],
            "PASS",
        )

    @patch("modules.network_checker.check_tcp_connection")
    @patch("modules.network_checker.resolve_dns")
    def test_overall_fail(
        self,
        mock_dns,
        mock_tcp,
    ):

        mock_dns.return_value = {
            "success": True,
            "ip_addresses": ["192.0.2.10"],
            "error": None,
        }

        mock_tcp.return_value = {
            "success": False,
            "connection_time_ms": None,
            "error": "Connection refused",
        }

        result = run_network_diagnostic(
            "example.com",
            443,
        )

        self.assertEqual(
            result["overall_status"],
            "FAIL",
        )


if __name__ == "__main__":
    unittest.main()