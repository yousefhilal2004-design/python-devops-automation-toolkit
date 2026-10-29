"""
Network Diagnostic Module

Features:
- DNS resolution
- TCP connectivity checks
- TCP connection timing
- Input validation
- Network error handling
- JSON output
- Command-line arguments
"""

import argparse
import json
import socket
import time
from datetime import datetime, timezone


# ==========================================
# 1. Validate Hostname
# ==========================================

def validate_host(host):
    """
    Validate the hostname or IP address.

    Returns a cleaned hostname.
    Raises ValueError for invalid input.
    """

    if not isinstance(host, str):
        raise ValueError("Host must be a string")

    host = host.strip()

    if not host:
        raise ValueError("Host cannot be empty")

    if any(character.isspace() for character in host):
        raise ValueError("Host cannot contain whitespace")

    if len(host) > 253:
        raise ValueError("Host is too long")

    return host


# ==========================================
# 2. Validate Port
# ==========================================

def validate_port(port):
    """
    Validate a TCP port number.

    Valid ports: 1-65535
    """

    if isinstance(port, bool):
        raise ValueError("Port must be an integer")

    try:
        port = int(port)
    except (TypeError, ValueError):
        raise ValueError("Port must be an integer") from None

    if not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535")

    return port


# ==========================================
# 3. Validate Timeout
# ==========================================

def validate_timeout(timeout):
    """
    Validate connection timeout.
    """

    try:
        timeout = float(timeout)
    except (TypeError, ValueError):
        raise ValueError("Timeout must be a number") from None

    if not 0 < timeout <= 60:
        raise ValueError("Timeout must be greater than 0 and at most 60")

    return timeout


# ==========================================
# 4. DNS Resolution
# ==========================================

def resolve_dns(host):
    """
    Resolve hostname to IPv4/IPv6 addresses.

    Returns structured DNS information.
    """

    host = validate_host(host)

    try:
        results = socket.getaddrinfo(
            host,
            None,
            type=socket.SOCK_STREAM,
        )

        ip_addresses = sorted({
            item[4][0]
            for item in results
        })

        return {
            "host": host,
            "success": True,
            "ip_addresses": ip_addresses,
            "error": None,
        }

    except socket.gaierror as error:
        return {
            "host": host,
            "success": False,
            "ip_addresses": [],
            "error": f"DNS resolution failed: {error}",
        }


# ==========================================
# 5. TCP Connectivity
# ==========================================

def check_tcp_connection(host, port, timeout=3):
    """
    Attempt a TCP connection to a host and port.

    Measures elapsed time.
    """

    host = validate_host(host)
    port = validate_port(port)
    timeout = validate_timeout(timeout)

    start_time = time.perf_counter()

    try:
        with socket.create_connection(
            (host, port),
            timeout=timeout,
        ):
            elapsed = time.perf_counter() - start_time

            return {
                "host": host,
                "port": port,
                "success": True,
                "connection_time_ms": round(elapsed * 1000, 2),
                "error": None,
            }

    except socket.timeout:
        return {
            "host": host,
            "port": port,
            "success": False,
            "connection_time_ms": None,
            "error": "Connection timed out",
        }

    except ConnectionRefusedError:
        return {
            "host": host,
            "port": port,
            "success": False,
            "connection_time_ms": None,
            "error": "Connection refused",
        }

    except OSError as error:
        return {
            "host": host,
            "port": port,
            "success": False,
            "connection_time_ms": None,
            "error": f"Connection failed: {error}",
        }


# ==========================================
# 6. Complete Network Diagnostic
# ==========================================

def run_network_diagnostic(host, port, timeout=3):
    """
    Run DNS resolution and TCP connectivity checks.
    """

    host = validate_host(host)
    port = validate_port(port)
    timeout = validate_timeout(timeout)

    dns_result = resolve_dns(host)

    tcp_result = check_tcp_connection(
        host,
        port,
        timeout,
    )

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host": host,
        "port": port,
        "timeout_seconds": timeout,
        "dns": dns_result,
        "tcp": tcp_result,
        "overall_status": (
            "PASS"
            if tcp_result["success"]
            else "FAIL"
        ),
    }


# ==========================================
# 7. Command-Line Interface
# ==========================================

def main():
    """
    Run network diagnostic from terminal.
    """

    parser = argparse.ArgumentParser(
        description="Python DevOps Network Diagnostic Tool"
    )

    parser.add_argument(
        "--host",
        required=True,
        help="Hostname or IP address",
    )

    parser.add_argument(
        "--port",
        required=True,
        type=int,
        help="TCP port number",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=3,
        help="Connection timeout in seconds (default: 3)",
    )

    args = parser.parse_args()

    try:
        result = run_network_diagnostic(
            args.host,
            args.port,
            args.timeout,
        )

    except ValueError as error:
        parser.error(str(error))

    print(json.dumps(result, indent=4))

    return 0 if result["tcp"]["success"] else 1


# ==========================================
# 8. Program Entry Point
# ==========================================

if __name__ == "__main__":
    raise SystemExit(main())