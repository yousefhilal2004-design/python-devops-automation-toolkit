import unittest

from unittest.mock import Mock, patch

import requests

from modules.website_checker import (
    check_website,
    is_healthy_status,
    validate_expected_status,
    validate_timeout,
    validate_url,
)


# ==========================================
# 1. URL Validation Tests
# ==========================================

class TestURLValidation(unittest.TestCase):

    def test_valid_https_url(self):
        self.assertEqual(
            validate_url("https://example.com"),
            "https://example.com",
        )

    def test_valid_http_url(self):
        self.assertEqual(
            validate_url("http://example.com"),
            "http://example.com",
        )

    def test_empty_url(self):
        with self.assertRaises(ValueError):
            validate_url("")

    def test_missing_scheme(self):
        with self.assertRaises(ValueError):
            validate_url("example.com")

    def test_invalid_scheme(self):
        with self.assertRaises(ValueError):
            validate_url("ftp://example.com")

    def test_url_with_spaces(self):
        with self.assertRaises(ValueError):
            validate_url("https://example .com")

    def test_url_with_credentials(self):
        with self.assertRaises(ValueError):
            validate_url(
                "https://user:password@example.com"
            )

    def test_invalid_port(self):
        with self.assertRaises(ValueError):
            validate_url(
                "https://example.com:99999"
            )


# ==========================================
# 2. Timeout Tests
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

    def test_invalid_timeout_type(self):
        with self.assertRaises(ValueError):
            validate_timeout("invalid")


# ==========================================
# 3. Expected Status Tests
# ==========================================

class TestExpectedStatus(unittest.TestCase):

    def test_default_expected_status(self):
        self.assertIsNone(
            validate_expected_status(None)
        )

    def test_valid_expected_status(self):
        self.assertEqual(
            validate_expected_status(204),
            204,
        )

    def test_invalid_expected_status(self):
        with self.assertRaises(ValueError):
            validate_expected_status(700)


# ==========================================
# 4. Health Status Tests
# ==========================================

class TestHealthStatus(unittest.TestCase):

    def test_status_200(self):
        self.assertTrue(
            is_healthy_status(200)
        )

    def test_status_301(self):
        self.assertTrue(
            is_healthy_status(301)
        )

    def test_status_404(self):
        self.assertFalse(
            is_healthy_status(404)
        )

    def test_status_503(self):
        self.assertFalse(
            is_healthy_status(503)
        )

    def test_expected_status_matches(self):
        self.assertTrue(
            is_healthy_status(
                204,
                expected_status=204,
            )
        )

    def test_expected_status_mismatch(self):
        self.assertFalse(
            is_healthy_status(
                200,
                expected_status=204,
            )
        )


# ==========================================
# 5. HTTP Request Tests
# ==========================================

class TestWebsiteChecker(unittest.TestCase):

    @patch("modules.website_checker.requests.get")
    def test_healthy_website(self, mock_get):

        mock_response = Mock()

        mock_response.status_code = 200
        mock_response.url = "https://example.com"
        mock_response.history = []

        mock_get.return_value = mock_response

        result = check_website(
            "https://example.com"
        )

        self.assertTrue(result["healthy"])
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(
            result["health_status"],
            "HEALTHY",
        )

        mock_get.assert_called_once_with(
            "https://example.com",
            timeout=5.0,
            allow_redirects=True,
        )

    @patch("modules.website_checker.requests.get")
    def test_unhealthy_website(self, mock_get):

        mock_response = Mock()

        mock_response.status_code = 503
        mock_response.url = "https://example.com"
        mock_response.history = []

        mock_get.return_value = mock_response

        result = check_website(
            "https://example.com"
        )

        self.assertFalse(result["healthy"])
        self.assertEqual(result["status_code"], 503)
        self.assertEqual(
            result["health_status"],
            "UNHEALTHY",
        )

    @patch("modules.website_checker.requests.get")
    def test_redirect(self, mock_get):

        mock_response = Mock()

        mock_response.status_code = 200
        mock_response.url = "https://example.com/home"
        mock_response.history = [Mock(status_code=301)]

        mock_get.return_value = mock_response

        result = check_website(
            "https://example.com"
        )

        self.assertTrue(result["redirected"])
        self.assertEqual(result["redirect_count"], 1)
        self.assertEqual(
            result["final_url"],
            "https://example.com/home",
        )

    @patch("modules.website_checker.requests.get")
    def test_timeout(self, mock_get):

        mock_get.side_effect = requests.exceptions.Timeout()

        result = check_website(
            "https://example.com"
        )

        self.assertFalse(result["healthy"])
        self.assertEqual(
            result["error"],
            "HTTP request timed out",
        )

    @patch("modules.website_checker.requests.get")
    def test_connection_error(self, mock_get):

        mock_get.side_effect = (
            requests.exceptions.ConnectionError()
        )

        result = check_website(
            "https://example.com"
        )

        self.assertFalse(result["healthy"])
        self.assertEqual(
            result["error"],
            "HTTP connection failed",
        )

    @patch("modules.website_checker.requests.get")
    def test_ssl_error(self, mock_get):

        mock_get.side_effect = requests.exceptions.SSLError()

        result = check_website(
            "https://example.com"
        )

        self.assertFalse(result["healthy"])
        self.assertEqual(
            result["error"],
            "SSL/TLS certificate verification failed",
        )

    @patch("modules.website_checker.requests.get")
    def test_expected_status_success(self, mock_get):

        mock_response = Mock()

        mock_response.status_code = 204
        mock_response.url = "https://example.com"
        mock_response.history = []

        mock_get.return_value = mock_response

        result = check_website(
            "https://example.com",
            expected_status=204,
        )

        self.assertTrue(result["healthy"])
        self.assertEqual(result["expected_status"], 204)

    @patch("modules.website_checker.requests.get")
    def test_expected_status_failure(self, mock_get):

        mock_response = Mock()

        mock_response.status_code = 200
        mock_response.url = "https://example.com"
        mock_response.history = []

        mock_get.return_value = mock_response

        result = check_website(
            "https://example.com",
            expected_status=204,
        )

        self.assertFalse(result["healthy"])


if __name__ == "__main__":
    unittest.main()