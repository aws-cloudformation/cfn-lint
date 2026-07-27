"""
Cross-platform file locking for schema cache updates.

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import IO, Iterator

LOGGER = logging.getLogger(__name__)


@contextmanager
def file_lock(lock_path: Path, timeout: float = 300.0) -> Iterator[IO[str]]:
    """Acquire an exclusive file lock, blocking until available or timeout.

    Creates the lock file and parent directories if they don't exist.
    The lock is released when the context manager exits.

    Args:
        lock_path: Path to the lock file
        timeout: Maximum seconds to wait for the lock (default 5 minutes)

    Yields:
        The open lock file handle

    Raises:
        TimeoutError: If the lock cannot be acquired within timeout
        OSError: If lock file cannot be created or locked
    """
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    # Open in write mode to create if missing
    lock_file = open(lock_path, "w", encoding="utf-8")
    try:
        _acquire_lock(lock_file, timeout)
        yield lock_file
    finally:
        _release_lock(lock_file)
        lock_file.close()


def _acquire_lock(lock_file: IO[str], timeout: float) -> None:
    """Platform-specific lock acquisition with retry loop."""
    if sys.platform == "win32":  # pragma: no cover
        _acquire_lock_windows(lock_file, timeout)
    else:
        _acquire_lock_unix(lock_file, timeout)


def _acquire_lock_unix(lock_file: IO[str], timeout: float) -> None:
    """Acquire lock on Unix using fcntl.flock()."""
    import fcntl

    start = time.monotonic()
    while True:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            LOGGER.debug("Acquired schema cache lock")
            return
        except (BlockingIOError, OSError):
            if time.monotonic() - start >= timeout:
                raise TimeoutError(
                    f"Could not acquire schema cache lock within {timeout}s. "
                    "Another cfn-lint process may be updating the cache."
                )
            time.sleep(0.1)


def _acquire_lock_windows(
    lock_file: IO[str], timeout: float
) -> None:  # pragma: no cover
    """Acquire lock on Windows using msvcrt.locking()."""
    import msvcrt

    start = time.monotonic()
    while True:
        try:
            # Lock byte 0 with exclusive lock (non-blocking)
            msvcrt.locking(  # type: ignore[attr-defined]
                lock_file.fileno(),
                msvcrt.LK_NBLCK,  # type: ignore[attr-defined]
                1,
            )
            LOGGER.debug("Acquired schema cache lock")
            return
        except OSError:
            if time.monotonic() - start >= timeout:
                raise TimeoutError(
                    f"Could not acquire schema cache lock within {timeout}s. "
                    "Another cfn-lint process may be updating the cache."
                )
            time.sleep(0.1)


def _release_lock(lock_file: IO[str]) -> None:
    """Platform-specific lock release."""
    if sys.platform == "win32":  # pragma: no cover
        import msvcrt

        try:
            msvcrt.locking(  # type: ignore[attr-defined]
                lock_file.fileno(),
                msvcrt.LK_UNLCK,  # type: ignore[attr-defined]
                1,
            )
        except OSError:
            pass  # Already unlocked or file closed
    else:
        import fcntl

        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        except OSError:  # pragma: no cover
            pass  # Already unlocked or file closed
    LOGGER.debug("Released schema cache lock")
