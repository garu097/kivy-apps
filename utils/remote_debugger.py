#!/usr/bin/env python3
"""
Remote Debugger Helper Class using debugpy
"""

import contextlib
import os
import time
from typing import Optional

from utils.logging import get_logger
from utils.singleton import Singleton

logger_normal = get_logger(__name__)


class RemoteDebugger(Singleton):
    """
    Helper class for managing remote debugging with debugpy in multiprocessing environments.

    Uses Singleton pattern - each process has one debugger instance.
    No locks needed since each process has its own singleton instance.
    """

    def __init__(
        self,
        name: int,
        port: Optional[int] = None,
        host: str = "localhost",
        wait_for_client: bool = True,
        timeout: float = 30.0,
        auto_enable: bool = None,
    ):
        """
        Initialize remote debugger.

        Args:
            name: Unique name for this debugger instance
            port: Port number for debugpy server (auto-assigned if None)
            host: Host address for debugpy server
            wait_for_client: Whether to wait for debugger to attach
            timeout: Timeout for waiting for client (seconds)
            auto_enable: Auto-enable based on env var (None = check DEBUG_WORKER)
        """
        self.name = name
        self.host = host
        self.port = port
        self.wait_for_client = wait_for_client
        self.timeout = timeout
        self.logger = get_logger(
            __name__, extra={"job": name}
        )

        # Determine if debugging should be enabled
        if auto_enable is None:
            self.enabled = (
                os.getenv(
                    "DEBUG_WORKER", "false"
                ).lower()
                == "true"
            )
        else:
            self.enabled = auto_enable

        self.is_listening = False
        self.is_attached = False

    def start_server(self) -> bool:
        """
        Start debugpy server and optionally wait for client.

        Returns:
            bool: True if server started successfully
        """
        if not self.enabled:
            self.logger.info(f"{self.enabled=}")
            self.logger.debug(
                "Remote debugging disabled"
            )
            return False

        try:
            import debugpy
        except ImportError:
            self.logger.error(
                "debugpy not installed. Install with: pip install debugpy"
            )
            return False

        try:
            # Auto-assign port if not specified
            if self.port is None:
                self.port = (
                    self._get_available_port()
                )

            self.logger.info(
                f"🔧 Starting debug server on {self.host}:{self.port}"
            )

            # Start debugpy server
            debugpy.listen((self.host, self.port))
            self.is_listening = True

            self.logger.info(
                f"🔧 Debug server listening on {self.host}:{self.port}"
            )

            if self.wait_for_client:
                self.logger.info(
                    "🔧 Debug server ready. You can attach debugger now..."
                )

                # Check for client connection with timeout
                start_time = time.time()
                while (
                    time.time() - start_time
                    < self.timeout
                ):
                    if debugpy.is_client_connected():
                        self.is_attached = True
                        break
                    time.sleep(
                        0.1
                    )  # Check every 100ms

            return True

        except Exception as e:
            self.logger.error(
                f"Failed to start debug server: {e}"
            )
            return False

    def _get_available_port(self) -> int:
        """Get an available port for debugpy server."""
        base_port = int(
            os.getenv("DEBUG_PORT_BASE", "5678")
        )

        # Use hash of name to get consistent port for same worker
        worker_offset = self.name % 1000
        return base_port + worker_offset

    def is_debugger_connected(self) -> bool:
        """
        Check if debugger is currently connected.

        Returns:
            bool: True if debugger is connected
        """
        if not self.is_listening:
            self.logger.info(
                "🔧 Debug server not listening"
            )
            return False

        try:
            import debugpy

            connected = (
                debugpy.is_client_connected()
            )
            if connected and not self.is_attached:
                self.is_attached = True
            elif (
                not connected and self.is_attached
            ):
                self.is_attached = False
            return connected
        except Exception:
            return False

    def breakpoint(self, message: str = None):
        """
        Set a programmatic breakpoint if debugger is attached.

        Args:
            message: Optional message to log when breakpoint is hit
        """
        # Check current connection status
        if not self.is_debugger_connected():
            return

        if message:
            self.logger.info(
                f"🔧 Breakpoint: {message}"
            )

        try:
            import debugpy

            debugpy.breakpoint()
        except Exception as e:
            self.logger.error(
                f"Failed to set breakpoint: {e}"
            )

    def conditional_breakpoint(
        self, condition: bool, message: str = None
    ):
        """
        Set a breakpoint only if condition is True and debugger is connected.

        Args:
            condition: Condition to check before setting breakpoint
            message: Optional message to log
        """
        if (
            condition
            and self.is_debugger_connected()
        ):
            self.breakpoint(message)

    def debug_if_connected(
        self, func, *args, **kwargs
    ):
        """
        Execute debug function only if debugger is connected.

        Args:
            func: Function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
        """
        if self.is_debugger_connected():
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.logger.error(
                    f"Debug function failed: {e}"
                )
        return None

    def stop(self):
        """Stop the debug server."""
        if self.is_listening:
            self.logger.info(
                "🔧 Stopping debug server"
            )
            self.is_listening = False
            self.is_attached = False

    def __enter__(self):
        """Context manager entry."""
        self.start_server()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


# Convenience functions
def start_worker_debug(
    worker_name: int,
    port: Optional[int] = None,
    wait_for_client: bool = False,
) -> Optional[RemoteDebugger]:
    """
    Convenience function to start debugging for a worker using Singleton pattern.

    Args:
        worker_name: Name/ID of the worker
        port: Port number (auto-assigned if None)
        wait_for_client: Whether to wait for debugger to attach

    Returns:
        RemoteDebugger singleton instance or None if debugging disabled
    """
    # Don't create debugger if debugging is disabled
    if not is_debug_enabled():
        return None

    # Use singleton pattern - get existing instance or create new one
    debugger = RemoteDebugger.instance(
        name=worker_name,
        port=port,
        wait_for_client=wait_for_client,
    )

    # Start server if not already listening
    if not debugger.is_listening:
        debugger.start_server()

    return debugger


def is_debug_enabled() -> bool:
    """Check if debugging is enabled via environment variable."""
    return (
        os.getenv("DEBUG_WORKER", "false").lower()
        == "true"
    )


def get_current_debugger() -> Optional[
    RemoteDebugger
]:
    """Get the current singleton debugger instance."""
    try:
        # Get the singleton instance (returns None if not created yet)
        return RemoteDebugger.instance()
    except Exception as e:
        logger_normal.error(
            f"🔧 get_current_debugger, {e}"
        )
        return None


def debug_breakpoint(message: str = None):
    """
    Set a breakpoint if debugger is available and connected.

    Args:
        message: Optional message to log
    """
    import contextlib

    debugger = get_current_debugger()
    if debugger:
        with contextlib.suppress(Exception):
            debugger.breakpoint(message)


def debug_conditional_breakpoint(
    condition: bool, message: str = None
):
    """
    Set a conditional breakpoint if debugger is available.

    Args:
        condition: Condition to check
        message: Optional message to log
    """
    debugger = get_current_debugger()
    if debugger:
        with contextlib.suppress(Exception):
            debugger.conditional_breakpoint(
                condition, message
            )


def is_debugger_attached() -> bool:
    """
    Check if debugger is attached to current process.

    Returns:
        bool: True if debugger is attached
    """
    debugger = get_current_debugger()
    if debugger:
        try:
            return (
                debugger.is_debugger_connected()
            )
        except Exception:
            return False
    return False
