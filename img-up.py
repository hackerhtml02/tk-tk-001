import os
import base64
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

EMAIL = "newtk1@latterlavender.cfd"
PASSWORD = "Haris123@"


def login_only():
    with sync_playwright() as p:
        print("🚀 Launching Browser (Headful)...")

        browser = p.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--start-maximized"
            ]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            java_script_enabled=True
        )

        page = context.new_page()

        page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """)

        print("🌍 Opening Adobe sign-in page...")
        page.goto("https://account.adobe.com/sign-in", timeout=60000)

        try:
            print("🔎 Waiting for Google button...")
            page.wait_for_selector(
                'button[data-id="EmailPage-GoogleSignInButton"]',
                timeout=60000
            )

            print("🖱 Clicking Continue with Google...")

            # 👇 Capture new popup page
            with context.expect_page() as new_page_info:
                page.locator(
                    'button[data-id="EmailPage-GoogleSignInButton"]'
                ).click()

            google_page = new_page_info.value
            google_page.wait_for_load_state()

        except PlaywrightTimeoutError:
            print("❌ Google button not found!")
            browser.close()
            return

        # -------- EMAIL --------
        try:
            print("📧 Waiting for email field...")
            google_page.wait_for_selector('input[type="email"]', timeout=60000)
            google_page.fill('input[type="email"]', EMAIL)
            google_page.keyboard.press("Enter")

        except PlaywrightTimeoutError:
            print("❌ Email field not found!")
            browser.close()
            return

        # -------- PASSWORD --------
        try:
            print("🔐 Waiting for password field...")
            google_page.wait_for_selector('input[name="Passwd"]', timeout=60000)
            google_page.fill('input[name="Passwd"]', PASSWORD)
            google_page.keyboard.press("Enter")

        except PlaywrightTimeoutError:
            print("❌ Password field not found!")
            browser.close()
            return

        print("⏳ Waiting for Bearer token from network...")

        bearer_token = None

        try:
            while True:
                request = context.wait_for_event("request", timeout=120000)

                if "ims-na1.adobelogin.com/ims/profile" in request.url:
                    auth_header = request.headers.get("authorization")

                    if auth_header and auth_header.startswith("Bearer "):
                        bearer_token = auth_header.replace("Bearer ", "")
                        break

        except PlaywrightTimeoutError:
            print("❌ Timeout waiting for token!")
            browser.close()
            return

        if bearer_token:
            print("🟢 Token Captured!")

            encoded_token = base64.b64encode(
                bearer_token.encode()
            ).decode()

            with open("tk.txt", "w") as f:
                f.write(encoded_token)

            print("✅ Token saved to tk.txt (Base64 encoded)")

        print("🚪 Closing browser...")
        browser.close()


if __name__ == "__main__":
    login_only()
