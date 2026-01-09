"""
Pytest configuration for Playwright functional tests.

This module provides fixtures for running Playwright tests against
the Flet web application with isolated test data.

Note: Flutter web apps render to canvas, so we need to enable the
accessibility/semantics layer for Playwright to find elements.
"""

import pytest
import subprocess
import time
import socket
import tempfile
import shutil
import os
from pathlib import Path
from typing import Generator


def get_free_port() -> int:
    """Find an available port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def enable_flutter_semantics(page):
    """
    Enable Flutter's accessibility/semantics tree.
    
    Flutter web renders to canvas, making elements invisible to Playwright.
    Clicking the semantics placeholder enables the accessibility tree,
    which creates DOM elements that Playwright can interact with.
    """
    page.evaluate('''
        const placeholder = document.querySelector("flt-semantics-placeholder");
        if (placeholder) {
            placeholder.dispatchEvent(new MouseEvent("click", {bubbles: true, cancelable: true}));
        }
    ''')
    # Wait for semantics tree to populate
    time.sleep(1)


@pytest.fixture(scope="session")
def app_port() -> int:
    """Get a free port for the test server."""
    return get_free_port()


@pytest.fixture(scope="session")
def test_data_dir() -> Generator[Path, None, None]:
    """
    Create an isolated temporary directory for test data.
    
    This ensures tests don't interfere with the user's real app data.
    """
    # Create a temp directory for test data
    temp_dir = Path(tempfile.mkdtemp(prefix="abitus_test_"))
    
    yield temp_dir
    
    # Cleanup after all tests complete
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def app_server(app_port: int, test_data_dir: Path) -> Generator[str, None, None]:
    """
    Start the Flet app in web mode for testing.
    
    This fixture starts the app once per test session with isolated
    test data, and tears it down when all tests complete.
    """
    # Set environment variable to use isolated test data directory
    env = os.environ.copy()
    env["ABITUS_DATA_DIR"] = str(test_data_dir)
    
    # Start the Flet app in web mode
    process = subprocess.Popen(
        [
            "uv", "run", "flet", "run", "--web", "--port", str(app_port),
            "src/main.py"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    
    # Wait for the server to be ready (Flet takes a while to start)
    base_url = f"http://localhost:{app_port}"
    max_retries = 40  # 20 seconds
    for _ in range(max_retries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("localhost", app_port))
                break
        except ConnectionRefusedError:
            time.sleep(0.5)
    else:
        process.terminate()
        raise RuntimeError(f"Flet app did not start within {max_retries * 0.5}s")
    
    # Give Flutter/Flet extra time to fully initialize
    time.sleep(5)
    
    yield base_url
    
    # Cleanup
    process.terminate()
    process.wait(timeout=10)


@pytest.fixture
def page_with_app(page, app_server: str):
    """
    Provide a Playwright page navigated to the running Flet app.
    
    Usage:
        def test_something(page_with_app):
            page_with_app.get_by_text("Accept Quest").click()
    """
    page.goto(app_server, wait_until="networkidle")
    page.wait_for_selector("flutter-view", timeout=30000)
    time.sleep(2)  # Wait for app content to render
    enable_flutter_semantics(page)
    return page


@pytest.fixture
def fresh_app_page(page, app_server: str, test_data_dir: Path):
    """
    Provide a Playwright page with a completely fresh database.
    
    This fixture deletes the test database before navigating,
    ensuring a completely clean slate for each test that uses it.
    """
    # Delete the test database to start fresh
    db_path = test_data_dir / "abitus.db"
    if db_path.exists():
        db_path.unlink()
    
    page.goto(app_server, wait_until="networkidle")
    page.wait_for_selector("flutter-view", timeout=30000)
    
    # Reload to pick up the fresh database
    page.reload(wait_until="networkidle")
    page.wait_for_selector("flutter-view", timeout=30000)
    time.sleep(2)  # Wait for app content to render
    
    enable_flutter_semantics(page)
    return page


# Playwright configuration
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for testing."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},  # Match Flutter default
    }
