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

        # 🔥 Remove webdriver detection
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
            page.locator(
                'button[data-id="EmailPage-GoogleSignInButton"]'
            ).click()

        except PlaywrightTimeoutError:
            print("❌ Google button not found!")
            browser.close()
            return

        # -------- EMAIL --------
        try:
            print("📧 Waiting for email field...")
            page.wait_for_selector('input[type="email"]', timeout=60000)
            page.fill('input[type="email"]', EMAIL)
            page.keyboard.press("Enter")

        except PlaywrightTimeoutError:
            print("❌ Email field not found!")
            browser.close()
            return

        # ---------------- PASSWORD ----------------
        try:
            print("🔐 Waiting for password field...")

            # Better Google selector
            page.wait_for_selector('input[name="Passwd"]', timeout=60000)

            page.fill('input[name="Passwd"]', PASSWORD)
            page.keyboard.press("Enter")

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

            # 🔥 Base64 Encode
            encoded_token = base64.b64encode(
                bearer_token.encode()
            ).decode()

            # 🔥 Save to tk.txt
            with open("tk.txt", "w") as f:
                f.write(encoded_token)

            print("✅ Token saved to tk.txt (Base64 encoded)")

        print("🚪 Closing browser...")
        browser.close()


if __name__ == "__main__":
    login_only()
