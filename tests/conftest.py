"""
Pytest configuration for Playwright functional tests.

This module provides fixtures for running Playwright tests against
the Flet web application.
"""

import pytest
import subprocess
import time
import socket
from typing import Generator


def get_free_port() -> int:
    """Find an available port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def app_port() -> int:
    """Get a free port for the test server."""
    return get_free_port()


@pytest.fixture(scope="session")
def app_server(app_port: int) -> Generator[str, None, None]:
    """
    Start the Flet app in web mode for testing.
    
    This fixture starts the app once per test session and tears it down
    when all tests complete.
    """
    # Start the Flet app in web mode
    process = subprocess.Popen(
        [
            "flet", "run", "--web", "--port", str(app_port),
            "src/main.py"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    # Wait for the server to be ready
    base_url = f"http://localhost:{app_port}"
    max_retries = 30
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
    
    # Give Flutter/Flet a moment to fully initialize
    time.sleep(2)
    
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
            # page_with_app is already at the app URL
            page_with_app.get_by_label("accept-quest").click()
    """
    page.goto(app_server)
    # Wait for Flutter/Flet to fully render
    # Flet apps show a "flet-view" element when ready
    page.wait_for_selector("flet-view", timeout=30000)
    return page


# Playwright configuration
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for testing."""
    return {
        **browser_context_args,
        "viewport": {"width": 390, "height": 844},  # iPhone 12 Pro dimensions
    }

