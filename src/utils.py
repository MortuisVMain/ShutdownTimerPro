import socket
import sys

def check_single_instance(port=49152):
    """
    Ensures only one instance of the application runs at a time using a loopback socket lock.
    Returns the bound socket object if successful, or None if another instance is already running.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', port))
        return s
    except Exception:
        return None

def validate_timer_input(hours, minutes):
    """
    Validates and clamps hours (0..24) and minutes (0..59).
    Returns total seconds.
    """
    try:
        h = max(0, min(24, int(hours or 0)))
        m = max(0, min(59, int(minutes or 0)))
        return h * 3600 + m * 60
    except (ValueError, TypeError):
        return 0
