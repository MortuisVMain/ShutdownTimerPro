"""
Single Instance Mutex & IPC Module
Uses Windows Win32 Named Mutex for atomic process uniqueness and loopback IPC for window restoration.
"""

import ctypes
import socket
import threading
import logging

ERROR_ALREADY_EXISTS = 183
DEFAULT_MUTEX_NAME = "Global\\ShutdownTimerPro_SingleInstanceMutex_v2"
IPC_PORT = 49812

class SingleInstanceMutex:
    def __init__(self, mutex_name=DEFAULT_MUTEX_NAME, ipc_port=IPC_PORT):
        self.mutex_name = mutex_name
        self.ipc_port = ipc_port
        self.mutex_handle = None
        self.is_single = False
        self.server_socket = None

    def acquire(self) -> bool:
        """
        Attempts to acquire the named Win32 mutex.
        Returns True if this is the only running instance.
        """
        try:
            self.mutex_handle = ctypes.windll.kernel32.CreateMutexW(None, False, self.mutex_name)
            last_error = ctypes.windll.kernel32.GetLastError()
            if last_error == ERROR_ALREADY_EXISTS:
                logging.warning("SingleInstanceMutex: Another instance already holds the mutex.")
                self.is_single = False
                return False
            
            self.is_single = True
            self._start_ipc_listener()
            return True
        except Exception as e:
            logging.error(f"Error acquiring Win32 Mutex: {e}")
            self.is_single = False
            return False

    def _start_ipc_listener(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(("127.0.0.1", self.ipc_port))
            self.server_socket.listen(1)
        except Exception as e:
            logging.error(f"Failed to bind IPC listener socket: {e}")

    def listen_for_restore(self, callback):
        """Starts background listener to restore window when duplicate instance launches."""
        if not self.server_socket:
            return

        def listener():
            while self.is_single and self.server_socket:
                try:
                    conn, _ = self.server_socket.accept()
                    data = conn.recv(1024)
                    if data == b"RESTORE":
                        logging.info("Received RESTORE signal from duplicate process")
                        if callback:
                            callback()
                    conn.close()
                except Exception:
                    break

        t = threading.Thread(target=listener, daemon=True, name="IPCListenerThread")
        t.start()

    def notify_running_instance(self):
        """Sends signal to running instance to bring its window to focus."""
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(2.0)
            client.connect(("127.0.0.1", self.ipc_port))
            client.sendall(b"RESTORE")
            client.close()
            logging.info("Signaled existing instance to RESTORE")
        except Exception as e:
            logging.error(f"Could not signal existing instance: {e}")

    def release(self):
        """Releases the mutex and closes IPC socket."""
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception as e:
                logging.error(f"Error closing IPC socket: {e}")
        if self.mutex_handle:
            try:
                ctypes.windll.kernel32.CloseHandle(self.mutex_handle)
                self.mutex_handle = None
            except Exception as e:
                logging.error(f"Error closing Mutex handle: {e}")
