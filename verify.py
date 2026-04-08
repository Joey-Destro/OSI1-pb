from playwright.sync_api import sync_playwright

def run_cuj(page):
    page.goto("http://localhost:7860")
    page.wait_for_timeout(2000)

    # Take screenshot at the key moment showing the app loaded
    page.screenshot(path="verification.png")
    page.wait_for_timeout(1000)

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="."
        )
        page = context.new_page()
        try:
            run_cuj(page)
        finally:
            context.close()  # MUST close context to save the video
            browser.close()
