import asyncio
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
            # Add flags useful for containers environments:
            #  - --no-sandbox: required when running as non-root or in restricted environments
            #  - --disable-dev-shm-usage: avoids /dev/shm size issues in containers
            #  - --disable-gpu: recommended for headless
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"],
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
            try:
                await self.browser.close()
            except Exception as e:
                print(f"Warning: browser already closed or invalid → {e}")
            self.browser = None

        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception as e:
                print(f"Warning: playwright already stopped → {e}")
            self.playwright = None

    async def get_browser(self):
        """Ensure browser is started and return it."""
        if self.browser is None:
            await self.start()
        try:
            is_connected_fn = getattr(self.browser, "is_connected", None)
            if is_connected_fn:
                result = is_connected_fn()
                if asyncio.iscoroutine(result):
                    is_connected = await result
                else:
                    is_connected = bool(result)
            else:
                # If no is_connected, assume browser is valid
                is_connected = True
        except Exception:
            is_connected = False

        if not is_connected:
            # Attempt to restart browser once
            try:
                await self.stop()
            except Exception:
                pass
            await self.start()

        return self.browser


# Create a single shared instance
browser_manager = BrowserManager()
