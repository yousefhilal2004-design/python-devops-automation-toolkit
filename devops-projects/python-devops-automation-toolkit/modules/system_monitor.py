import json
import time
from datetime import datetime

import psutil


# ==========================================
# 1. Convert Bytes to GiB
# ==========================================

def bytes_to_gb(value):
    """Convert bytes to GiB (binary gigabytes)."""
    return round(value / (1024 ** 3), 2)


# ==========================================
# 2. CPU Monitoring
# ==========================================

def get_cpu_usage():
    """Measure CPU usage over one second."""
    return psutil.cpu_percent(interval=1)


# ==========================================
# 3. Memory Monitoring
# ==========================================

def get_memory_usage():
    """Return memory usage information."""
    memory = psutil.virtual_memory()

    return {
        "total_gb": bytes_to_gb(memory.total),
        "used_gb": bytes_to_gb(memory.used),
        "available_gb": bytes_to_gb(memory.available),
        "percent": memory.percent,
    }


# ==========================================
# 4. Disk Monitoring
# ==========================================

def get_disk_usage():
    """Return root filesystem disk usage."""
    disk = psutil.disk_usage("/")

    return {
        "total_gb": bytes_to_gb(disk.total),
        "used_gb": bytes_to_gb(disk.used),
        "free_gb": bytes_to_gb(disk.free),
        "percent": disk.percent,
    }


# ==========================================
# 5. System Uptime
# ==========================================

def get_system_uptime():
    """Return system uptime in seconds."""
    boot_time = psutil.boot_time()
    uptime = time.time() - boot_time

    return round(uptime, 2)


# ==========================================
# 6. Collect System Information
# ==========================================

def get_system_info():
    """Collect CPU, memory, disk, and uptime information."""

    return {
        "timestamp": datetime.now().astimezone().isoformat(),
        "cpu_percent": get_cpu_usage(),
        "memory": get_memory_usage(),
        "disk": get_disk_usage(),
        "uptime_seconds": get_system_uptime(),
    }


# ==========================================
# 7. Check Resource Thresholds
# ==========================================

def check_thresholds(system_info):
    """Check system resources against warning thresholds."""

    warnings = []

    cpu = system_info["cpu_percent"]
    memory = system_info["memory"]["percent"]
    disk = system_info["disk"]["percent"]

    if cpu >= 80:
        warnings.append("WARNING: High CPU usage")

    if memory >= 85:
        warnings.append("WARNING: High memory usage")

    if disk >= 90:
        warnings.append("WARNING: High disk usage")

    if not warnings:
        warnings.append(
            "System resource usage is below warning thresholds"
        )

    return warnings


# ==========================================
# 8. Main Program
# ==========================================

if __name__ == "__main__":

    # Collect monitoring data
    information = get_system_info()

    # Add threshold results to JSON
    information["warnings"] = check_thresholds(information)

    # Display formatted JSON
    print(json.dumps(information, indent=4))