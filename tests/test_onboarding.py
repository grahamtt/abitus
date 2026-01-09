"""
Playwright tests for the onboarding/interview flow.

These tests verify the initial user experience when first launching the app.

Note: Since Flet 0.80.x doesn't support semantics_label on controls,
we use text-based locators (get_by_text) for finding elements.
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_interview_loads(page_with_app: Page):
    """Verify the interview screen loads for new users."""
    # The interview should show the first category introduction
    # Look for the "Begin" button which appears on category intro screens
    begin_button = page_with_app.get_by_text("Begin")
    expect(begin_button).to_be_visible(timeout=10000)


@pytest.mark.e2e
def test_complete_interview_flow(page_with_app: Page):
    """Test completing the full interview assessment."""
    page = page_with_app
    
    # Start the first category
    page.get_by_text("Begin").click()
    
    # Answer questions by clicking continue/skip through them
    # The interview has multiple categories with multiple questions each
    max_questions = 50  # Safety limit
    questions_answered = 0
    
    while questions_answered < max_questions:
        # Check if we're on a category intro (has "Begin" button)
        begin_button = page.get_by_text("Begin", exact=True)
        if begin_button.is_visible():
            begin_button.click()
            page.wait_for_timeout(300)
            continue
        
        # Check if we're on the completion screen (has "Begin Your Adventure!" button)
        adventure_button = page.get_by_text("Begin Your Adventure!")
        if adventure_button.is_visible():
            break
        
        # We're on a question - click continue/skip
        continue_button = page.get_by_text("Continue")
        skip_button = page.get_by_text("Skip")
        
        if continue_button.is_visible():
            continue_button.click()
            questions_answered += 1
            page.wait_for_timeout(300)
        elif skip_button.is_visible():
            skip_button.click()
            questions_answered += 1
            page.wait_for_timeout(300)
        else:
            # Something unexpected - break to avoid infinite loop
            break
    
    # We should now be on the completion screen
    expect(page.get_by_text("Begin Your Adventure!")).to_be_visible()
    
    # Enter a character name - find the text field by its label
    name_input = page.locator('input[type="text"]').first
    expect(name_input).to_be_visible()
    name_input.fill("Test Hero")
    
    # Start the adventure
    page.get_by_text("Begin Your Adventure!").click()
    
    # Should now see the main navigation (Home tab)
    expect(page.get_by_text("Home")).to_be_visible(timeout=10000)


@pytest.mark.smoke
def test_interview_navigation(page_with_app: Page):
    """Test back navigation during interview."""
    page = page_with_app
    
    # Start first category
    page.get_by_text("Begin").click()
    page.wait_for_timeout(500)
    
    # Answer a question (click Continue or Skip)
    continue_btn = page.get_by_text("Continue")
    skip_btn = page.get_by_text("Skip")
    
    if continue_btn.is_visible():
        continue_btn.click()
    elif skip_btn.is_visible():
        skip_btn.click()
    
    page.wait_for_timeout(500)
    
    # Go back
    back_button = page.get_by_text("Back")
    if back_button.is_visible():
        back_button.click()
        page.wait_for_timeout(500)
        # Should still be able to continue (back on previous question)
        expect(page.get_by_text("Continue").or_(page.get_by_text("Skip"))).to_be_visible()
