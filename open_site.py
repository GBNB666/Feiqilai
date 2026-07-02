"""Open the paper formatter site and take a screenshot."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:5173", wait_until="networkidle")
    page.screenshot(path="C:/Users/博博/paper-formatter/site_screenshot.png", full_page=True)
    print("OK: Screenshot saved to site_screenshot.png")
    browser.close()
