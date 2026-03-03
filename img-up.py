import os
import base64
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

EMAIL = "newtk1@latterlavender.cfd"
PASSWORD = "Haris123@"

def login_only():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        )

        context = browser.new_context()
        page = context.new_page()

        print("Opening Adobe sign-in page...")
        page.goto("https://account.adobe.com/sign-in", timeout=60000)

        try:
            page.wait_for_selector(
                'button[data-id="EmailPage-GoogleSignInButton"]',
                timeout=60000
            )
            page.locator(
                'button[data-id="EmailPage-GoogleSignInButton"]'
            ).click()

        except PlaywrightTimeoutError:
            print("Google button not found!")
            browser.close()
            return

        # EMAIL
        try:
            page.wait_for_selector('input[type="email"]', timeout=30000)
            page.fill('input[type="email"]', EMAIL)
            page.keyboard.press("Enter")
        except PlaywrightTimeoutError:
            print("Email field not found!")
            browser.close()
            return

        # PASSWORD
        try:
            page.wait_for_selector('input[type="password"]', timeout=30000)
            page.fill('input[type="password"]', PASSWORD)
            page.keyboard.press("Enter")
        except PlaywrightTimeoutError:
            print("Password field not found!")
            browser.close()
            return

        print("Waiting for Bearer token...")

        bearer_token = None

        try:
            while True:
                request = context.wait_for_event("request", timeout=60000)

                if "ims-na1.adobelogin.com/ims/profile" in request.url:
                    auth_header = request.headers.get("authorization")

                    if auth_header and auth_header.startswith("Bearer "):
                        bearer_token = auth_header.replace("Bearer ", "")
                        break

        except PlaywrightTimeoutError:
            print("Timeout waiting for token!")
            browser.close()
            return

        if bearer_token:
            # 🔥 BASE64 ENCODE
            encoded = base64.b64encode(
                bearer_token.encode()
            ).decode()

            # 🔥 SAVE TO FILE
            with open("tk.txt", "w") as f:
                f.write(encoded)

            print("Token saved to tk.txt (Base64 encoded)")

        browser.close()


if __name__ == "__main__":
    login_only()
