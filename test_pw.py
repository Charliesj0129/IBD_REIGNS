from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://127.0.0.1:8503")
        time.sleep(5)
        # Try to find the iframe
        iframe_element = page.locator("iframe").first
        if iframe_element:
            frame = iframe_element.content_frame
            text = frame.locator("#card-text").inner_text()
            print("IFRAME CARD TEXT:", text)
            print("IFRAME FULL HTML:", frame.content()[:500])
        else:
            print("NO IFRAME FOUND")
        page.screenshot(path="screenshot.png")
        browser.close()

if __name__ == "__main__":
    run()
