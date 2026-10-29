"""
System Monitoring Module

Python DevOps Automation Toolkit

Features:
- System information
- CPU monitoring
- Memory monitoring
- Disk monitoring
- System uptime
- Configurable resource thresholds
- JSON output

Stage 2 - Updated for Stage 9 Integration
"""

import json
import platform
import socket

from datetime import datetime, timezone

import psutil


# ==========================================
# 1. Generate Timestamp
# ==========================================

def get_timestamp():
    """
    Return current UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()


# ==========================================
# 2. CPU Information
# ==========================================

def get_cpu_info():
    """
    Return CPU usage information.
    """

    return {
        "percent": psutil.cpu_percent(
            interval=0.5
        ),
        "physical_cores": psutil.cpu_count(
            logical=False
        ),
        "logical_cores": psutil.cpu_count(
            logical=True
        ),
    }


# ==========================================
# 3. Memory Information
# ==========================================

def get_memory_info():
    """
    Return memory usage information.
    """

    memory = psutil.virtual_memory()

    return {
        "total_gb": round(
            memory.total / (1024 ** 3),
            2,
        ),
        "available_gb": round(
            memory.available / (1024 ** 3),
            2,
        ),
        "used_gb": round(
            memory.used / (1024 ** 3),
            2,
        ),
        "percent": memory.percent,
    }


# ==========================================
# 4. Disk Information
# ==========================================

def get_disk_info():
    """
    Return disk usage information.
    """

    disk = psutil.disk_usage("/")

    return {
        "total_gb": round(
            disk.total / (1024 ** 3),
            2,
        ),
        "used_gb": round(
            disk.used / (1024 ** 3),
            2,
        ),
        "free_gb": round(
            disk.free / (1024 ** 3),
            2,
        ),
        "percent": disk.percent,
    }


# ==========================================
# 5. System Uptime
# ==========================================

def get_uptime():
    """
    Return system uptime information.
    """

    boot_time = psutil.boot_time()

    now = datetime.now(
        timezone.utc
    ).timestamp()

    uptime_seconds = max(
        0,
        int(now - boot_time),
    )

    days, remainder = divmod(
        uptime_seconds,
        86400,
    )

    hours, remainder = divmod(
        remainder,
        3600,
    )

    minutes, seconds = divmod(
        remainder,
        60,
    )

    return {
        "boot_time": datetime.fromtimestamp(
            boot_time,
            timezone.utc,
        ).isoformat(),
        "uptime_seconds": uptime_seconds,
        "uptime_formatted": (
            f"{days}d {hours}h "
            f"{minutes}m {seconds}s"
        ),
    }


# ==========================================
# 6. Complete System Information
# ==========================================

def get_system_info():
    """
    Collect system monitoring information.

    Returns a JSON-compatible dictionary.
    """

    cpu = get_cpu_info()

    return {
        "timestamp": get_timestamp(),
        "hostname": socket.gethostname(),
        "operating_system": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "cpu_percent": cpu["percent"],
        "cpu": cpu,
        "memory": get_memory_info(),
        "disk": get_disk_info(),
        "uptime": get_uptime(),
    }


# ==========================================
# 7. Validate Threshold
# ==========================================

def validate_threshold(value, name):
    """
    Validate resource threshold values.

    Valid range:
        0 < threshold <= 100
    """

    if isinstance(value, bool):
        raise ValueError(
            f"{name} must be a number"
        )

    if not isinstance(
        value,
        (int, float),
    ):
        raise ValueError(
            f"{name} must be a number"
        )

    if not 0 < value <= 100:
        raise ValueError(
            f"{name} must be between 0 and 100"
        )

    return value


# ==========================================
# 8. Check Resource Thresholds
# ==========================================

def check_thresholds(
    system_info,
    cpu_threshold=80,
    memory_threshold=85,
    disk_threshold=90,
):
    """
    Check system resources against thresholds.

    Default thresholds:
        CPU: 80%
        Memory: 85%
        Disk: 90%

    Thresholds can be customized through
    the application's configuration.
    """

    validate_threshold(
        cpu_threshold,
        "CPU threshold",
    )

    validate_threshold(
        memory_threshold,
        "Memory threshold",
    )

    validate_threshold(
        disk_threshold,
        "Disk threshold",
    )

    warnings = []

    cpu = system_info["cpu_percent"]

    memory = system_info["memory"]["percent"]

    disk = system_info["disk"]["percent"]

    if cpu >= cpu_threshold:
        warnings.append(
            "WARNING: High CPU usage"
        )

    if memory >= memory_threshold:
        warnings.append(
            "WARNING: High memory usage"
        )

    if disk >= disk_threshold:
        warnings.append(
            "WARNING: High disk usage"
        )

    if not warnings:
        warnings.append(
            "System resource usage is below warning thresholds"
        )

    return warnings


# ==========================================
# 9. Main Program
# ==========================================

def main():
    """
    Run standalone system monitoring.
    """

    information = get_system_info()

    information["warnings"] = check_thresholds(
        information
    )

    print(
        json.dumps(
            information,
            indent=4,
        )
    )


if __name__ == "__main__":
    main()