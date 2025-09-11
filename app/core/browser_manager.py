from playwright.async_api import async_playwright

playwright = None
browser = None

async def start_browser():
    global playwright, browser
    if browser is not None:
        return  # already started

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)

async def stop_browser():
    global browser, playwright
    if browser:
        await browser.close()
        browser = None
    if playwright:
        await playwright.stop()
        playwright = None

async def get_browser():
    """Ensure browser is started and return it."""
    global browser
    if browser is None:
        await start_browser()
    return browser
