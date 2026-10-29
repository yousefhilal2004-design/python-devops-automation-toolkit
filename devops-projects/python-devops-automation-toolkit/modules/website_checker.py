"""
Website Health Checker Module

Python DevOps Automation Toolkit

Features:
- URL validation
- HTTP/HTTPS requests
- HTTP status code checks
- Response time measurement
- Redirect handling
- Timeout handling
- Connection error handling
- SSL certificate verification
- Expected HTTP status support
- JSON output
- CLI arguments
- Exit codes
"""

import argparse
import json
import math
import time

from datetime import datetime, timezone
from urllib.parse import urlparse

import requests


# ==========================================
# 1. Validate URL
# ==========================================

def validate_url(url):
    """
    Validate an HTTP or HTTPS URL.

    Returns the cleaned URL.
    """

    if not isinstance(url, str):
        raise ValueError("URL must be a string")

    url = url.strip()

    if not url:
        raise ValueError("URL cannot be empty")

    if any(character.isspace() for character in url):
        raise ValueError("URL cannot contain whitespace")

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError(
            "URL must start with http:// or https://"
        )

    if not parsed.hostname:
        raise ValueError("URL must contain a valid hostname")

    try:
        port = parsed.port
    except ValueError:
        raise ValueError("URL contains an invalid port") from None

    if port is not None and not 1 <= port <= 65535:
        raise ValueError("URL port must be between 1 and 65535")

    if parsed.username is not None or parsed.password is not None:
        raise ValueError("Credentials must not be included in the URL")

    return url


# ==========================================
# 2. Validate Timeout
# ==========================================

def validate_timeout(timeout):
    """
    Validate HTTP request timeout.
    """

    if isinstance(timeout, bool):
        raise ValueError("Timeout must be a number")

    try:
        timeout = float(timeout)
    except (TypeError, ValueError):
        raise ValueError("Timeout must be a number") from None

    if not math.isfinite(timeout) or not 0 < timeout <= 60:
        raise ValueError(
            "Timeout must be greater than 0 and at most 60"
        )

    return timeout


# ==========================================
# 3. Validate Expected Status
# ==========================================

def validate_expected_status(expected_status):
    """
    Validate an optional expected HTTP status code.
    """

    if expected_status is None:
        return None

    if isinstance(expected_status, bool):
        raise ValueError("Expected status must be an integer")

    try:
        expected_status = int(expected_status)
    except (TypeError, ValueError):
        raise ValueError("Expected status must be an integer") from None

    if not 100 <= expected_status <= 599:
        raise ValueError(
            "Expected status must be between 100 and 599"
        )

    return expected_status


# ==========================================
# 4. Determine Health Status
# ==========================================

def is_healthy_status(status_code, expected_status=None):
    """
    Determine whether an HTTP status is healthy.

    Default:
        200-399 = healthy

    If expected_status is provided:
        Only that exact status is healthy.
    """

    if expected_status is not None:
        return status_code == expected_status

    return 200 <= status_code < 400


# ==========================================
# 5. Check Website Health
# ==========================================

def check_website(
    url,
    timeout=5,
    expected_status=None,
):
    """
    Send an HTTP GET request and return health information.
    """

    url = validate_url(url)
    timeout = validate_timeout(timeout)
    expected_status = validate_expected_status(
        expected_status
    )

    timestamp = datetime.now(timezone.utc).isoformat()

    result = {
        "timestamp": timestamp,
        "url": url,
        "final_url": None,
        "status_code": None,
        "response_time_ms": None,
        "healthy": False,
        "health_status": "UNHEALTHY",
        "redirected": False,
        "redirect_count": 0,
        "expected_status": expected_status,
        "error": None,
    }

    start_time = time.perf_counter()

    try:
        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
        )

        elapsed = time.perf_counter() - start_time

        healthy = is_healthy_status(
            response.status_code,
            expected_status,
        )

        result.update({
            "final_url": response.url,
            "status_code": response.status_code,
            "response_time_ms": round(
                elapsed * 1000,
                2,
            ),
            "healthy": healthy,
            "health_status": (
                "HEALTHY" if healthy else "UNHEALTHY"
            ),
            "redirected": len(response.history) > 0,
            "redirect_count": len(response.history),
        })

    except requests.exceptions.Timeout:
        result["error"] = "HTTP request timed out"

    except requests.exceptions.SSLError:
        result["error"] = "SSL/TLS certificate verification failed"

    except requests.exceptions.TooManyRedirects:
        result["error"] = "Too many HTTP redirects"

    except requests.exceptions.ConnectionError:
        result["error"] = "HTTP connection failed"

    except requests.exceptions.RequestException:
        result["error"] = "HTTP request failed"

    return result


# ==========================================
# 6. Command-Line Interface
# ==========================================

def main():
    """
    Run the website checker from the terminal.
    """

    parser = argparse.ArgumentParser(
        description="Python DevOps Website Health Checker"
    )

    parser.add_argument(
        "--url",
        required=True,
        help="Website URL to check",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=5,
        help="HTTP timeout in seconds (default: 5)",
    )

    parser.add_argument(
        "--expected-status",
        type=int,
        default=None,
        help="Optional expected HTTP status code",
    )

    args = parser.parse_args()

    try:
        result = check_website(
            url=args.url,
            timeout=args.timeout,
            expected_status=args.expected_status,
        )

    except ValueError as error:
        parser.error(str(error))

    print(json.dumps(result, indent=4))

    return 0 if result["healthy"] else 1


# ==========================================
# 7. Program Entry Point
# ==========================================

if __name__ == "__main__":
    raise SystemExit(main())