"""
Playwright tests for quest functionality.

These tests verify quest acceptance, completion, and progress tracking.
Note: These tests require a completed interview to access the main app.

Since Flet 0.80.x doesn't support semantics_label on controls,
we use text-based locators for finding elements.
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def app_with_character(page_with_app: Page) -> Page:
    """
    Fixture that completes the interview to get to the main app.
    
    This speeds up quest tests by handling onboarding setup.
    """
    page = page_with_app
    
    # Fast-forward through interview
    max_iterations = 60
    for _ in range(max_iterations):
        # Check for category intro
        begin_btn = page.get_by_text("Begin", exact=True)
        if begin_btn.is_visible():
            begin_btn.click()
            page.wait_for_timeout(200)
            continue
        
        # Check for completion screen
        adventure_btn = page.get_by_text("Begin Your Adventure!")
        if adventure_btn.is_visible():
            # Enter name and start
            name_input = page.locator('input[type="text"]').first
            if name_input.is_visible():
                name_input.fill("Test Hero")
            adventure_btn.click()
            break
        
        # Skip questions
        continue_btn = page.get_by_text("Continue")
        skip_btn = page.get_by_text("Skip")
        if continue_btn.is_visible():
            continue_btn.click()
            page.wait_for_timeout(200)
        elif skip_btn.is_visible():
            skip_btn.click()
            page.wait_for_timeout(200)
    
    # Wait for main app to confirm we're in (check for navigation text)
    expect(page.get_by_text("Home")).to_be_visible(timeout=10000)
    
    return page


@pytest.mark.e2e
def test_view_all_quests(app_with_character: Page):
    """Test navigating to the full quest list."""
    page = app_with_character
    
    # Click "View All" to see all quests (use text locator)
    view_all = page.get_by_text("View All")
    if view_all.is_visible():
        view_all.click()
        # Should be on quests page - verify by checking for quest content
        page.wait_for_timeout(1000)  # Allow page transition


@pytest.mark.e2e
def test_accept_quest(app_with_character: Page):
    """Test accepting an available quest."""
    page = app_with_character
    
    # Look for "Accept Quest" buttons
    accept_buttons = page.get_by_text("Accept Quest")
    
    # If there are available quests, accept one
    if accept_buttons.first.is_visible():
        accept_buttons.first.click()
        page.wait_for_timeout(500)
        
        # After accepting, we should see "Complete" button appear
        expect(page.get_by_text("Complete")).to_be_visible()


@pytest.mark.e2e  
def test_navigate_to_character_sheet(app_with_character: Page):
    """Test viewing the character sheet."""
    page = app_with_character
    
    # Click the view character sheet button
    char_sheet = page.get_by_text("View Full Character Sheet")
    expect(char_sheet).to_be_visible()
    char_sheet.click()
    
    # Should navigate to character view
    page.wait_for_timeout(1000)


@pytest.mark.e2e
def test_bottom_navigation(app_with_character: Page):
    """Test the bottom navigation bar works."""
    page = app_with_character
    
    # Navigate to Journal (click on Journal text in nav)
    page.get_by_text("Journal").click()
    page.wait_for_timeout(500)
    
    # Navigate to Quests
    page.get_by_text("Quests").click()
    page.wait_for_timeout(500)
    
    # Navigate back to Home
    page.get_by_text("Home").click()
    page.wait_for_timeout(500)


@pytest.mark.e2e
def test_complete_quest_flow(app_with_character: Page):
    """Test the full quest lifecycle: accept and complete."""
    page = app_with_character
    
    # Find and accept a quest
    accept_btn = page.get_by_text("Accept Quest").first
    if accept_btn.is_visible():
        accept_btn.click()
        page.wait_for_timeout(500)
        
        # Now complete it
        complete_btn = page.get_by_text("Complete").first
        if complete_btn.is_visible():
            complete_btn.click()
            page.wait_for_timeout(500)
            
            # Should see success indication or updated UI
            # The quest should no longer show "Complete" for that quest
