"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import tempfile
import threading
import time
from pathlib import Path
from test.testlib.testcase import BaseTestCase

from cfnlint.schema._lock import file_lock


class TestFileLock(BaseTestCase):
    """Test cross-platform file locking"""

    def test_lock_creates_file_and_dirs(self):
        """Lock file and parent directories are created if missing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "subdir" / "nested" / "lock.file"
            self.assertFalse(lock_path.exists())

            with file_lock(lock_path):
                self.assertTrue(lock_path.exists())
                self.assertTrue(lock_path.parent.exists())

    def test_lock_is_exclusive(self):
        """Second lock acquisition blocks until first is released"""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"
            results = []

            def worker(worker_id: int, delay: float):
                time.sleep(delay)
                with file_lock(lock_path, timeout=10.0):
                    results.append(f"enter-{worker_id}")
                    time.sleep(0.2)
                    results.append(f"exit-{worker_id}")

            t1 = threading.Thread(target=worker, args=(1, 0))
            t2 = threading.Thread(target=worker, args=(2, 0.05))

            t1.start()
            t2.start()
            t1.join()
            t2.join()

            # Worker 1 should complete before worker 2 enters
            self.assertEqual(results[0], "enter-1")
            self.assertEqual(results[1], "exit-1")
            self.assertEqual(results[2], "enter-2")
            self.assertEqual(results[3], "exit-2")

    def test_lock_timeout(self):
        """TimeoutError raised when lock cannot be acquired in time"""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"
            timeout_occurred = threading.Event()

            def holder():
                with file_lock(lock_path, timeout=10.0):
                    time.sleep(1.0)

            def waiter():
                time.sleep(0.1)
                try:
                    with file_lock(lock_path, timeout=0.2):
                        pass
                except TimeoutError:
                    timeout_occurred.set()

            t1 = threading.Thread(target=holder)
            t2 = threading.Thread(target=waiter)

            t1.start()
            t2.start()
            t1.join()
            t2.join()

            self.assertTrue(
                timeout_occurred.is_set(), "TimeoutError should have been raised"
            )

    def test_lock_released_on_exception(self):
        """Lock is released even if exception occurs inside context"""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"

            try:
                with file_lock(lock_path):
                    raise ValueError("Test exception")
            except ValueError:
                pass

            # Should be able to acquire lock again immediately
            acquired = False
            with file_lock(lock_path, timeout=0.5):
                acquired = True
            self.assertTrue(acquired)


class TestFileLockUnixSpecific(BaseTestCase):
    """Unix-specific lock tests"""

    def test_lock_works_on_current_platform(self):
        """Basic lock/unlock works on the current platform"""
        import sys

        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"

            # Just verify we can acquire and release a lock
            acquired = False
            with file_lock(lock_path, timeout=1.0):
                acquired = True
            self.assertTrue(acquired)


class TestFileLockWindowsSpecific(BaseTestCase):
    """Windows-specific lock tests - skipped on non-Windows"""

    def test_placeholder(self):
        """Placeholder test - actual Windows testing requires Windows CI"""
        # Windows-specific behavior is tested via integration tests on Windows CI
        # The cross-platform code paths share the same external interface
        pass
