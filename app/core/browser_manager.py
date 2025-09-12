from playwright.async_api import async_playwright

class BrowserManager:
    """
    Manages a shared Playwright browser instance.
    Ensures only one browser is running during app lifecycle.
    """

    def __init__(self):
        self.playwright = None
        self.browser = None

    async def start(self):
        """Start Playwright and launch Chromium if not already running."""
        if self.browser is not None:
            return self.browser  # already started

        self.playwright = await async_playwright().start()
        try:
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=["--disable-gpu", "--no-sandbox"],  # helps on Windows
                timeout=30000  # 30 seconds max
            )
        except Exception as e:
            await self.playwright.stop()
            self.playwright = None
            raise RuntimeError(f"Failed to launch browser: {e}") from e

        return self.browser

    async def stop(self):
        """Stop browser and Playwright instance."""
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    async def get_browser(self):
        """Ensure browser is started and return it."""
        if self.browser is None:
            await self.start()
        return self.browser


# Create a single shared instance
browser_manager = BrowserManager()
