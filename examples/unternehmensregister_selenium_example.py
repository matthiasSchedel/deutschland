"""
Example: Using Selenium to scrape unternehmensregister.de

This example demonstrates how to actually extract data from the website
using browser automation, since the site uses client-side rendering.

Requirements:
    pip install selenium webdriver-manager

Note: This is a working alternative to the requests-based approach,
which cannot handle JavaScript-rendered content.
"""

def example_with_selenium():
    """
    Working example using Selenium to extract company data.

    This overcomes the client-side rendering limitation.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        print("Error: Selenium not installed")
        print("Install with: pip install selenium webdriver-manager")
        return

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    print("Initializing browser...")

    try:
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Navigate to the website
        print("Loading unternehmensregister.de...")
        driver.get("https://www.unternehmensregister.de/de")

        # Wait for page to load
        wait = WebDriverWait(driver, 10)

        # Find search input
        print("Entering search query...")
        search_input = wait.until(
            EC.presence_of_element_located((By.ID, "quick_search:company_name"))
        )
        search_input.send_keys("Porsche")

        # Click search button
        search_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'][data-testid='globalSearchBtn']")
        search_button.click()

        # Wait for results page to load
        print("Waiting for results...")
        wait.until(EC.url_contains("/suche"))

        # Wait a bit more for JavaScript to render results
        import time
        time.sleep(3)

        # Try to find result elements (adjust selectors based on actual page structure)
        print("\nSearching for result elements...")

        # These selectors are examples - you'll need to inspect the actual page
        possible_selectors = [
            ".result-item",
            ".company-result",
            ".search-result",
            "[data-testid*='result']",
            ".card_card__L070q",  # From the HTML we saw earlier
        ]

        results_found = False
        for selector in possible_selectors:
            try:
                results = driver.find_elements(By.CSS_SELECTOR, selector)
                if results:
                    print(f"\n✓ Found {len(results)} elements with selector: {selector}")
                    results_found = True

                    # Try to extract text from first few results
                    for i, result in enumerate(results[:3], 1):
                        print(f"\nResult {i}:")
                        print(result.text[:200] + "..." if len(result.text) > 200 else result.text)
                    break
            except:
                continue

        if not results_found:
            print("\n⚠ No results found with standard selectors")
            print("This might mean:")
            print("1. The search returned no results")
            print("2. The page structure is different than expected")
            print("3. More wait time is needed for JavaScript to load")

            # Print page source for debugging
            print("\n--- Page Title ---")
            print(driver.title)

            print("\n--- Current URL ---")
            print(driver.current_url)

        # Close browser
        driver.quit()
        print("\n✓ Browser closed")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            driver.quit()
        except:
            pass


def example_simple_requests():
    """
    Show what happens with regular requests (for comparison).
    """
    print("=" * 70)
    print("Comparison: Using requests (doesn't work for dynamic content)")
    print("=" * 70)

    from deutschland.unternehmensregister import Unternehmensregister

    ur = Unternehmensregister()
    reports = ur.get_reports("Porsche", page_limit=1)

    print(f"\nResults found: {len(reports)}")
    print("Expected: 0 (because JavaScript is required)")

    if len(reports) == 0:
        print("\n✓ As expected - requests cannot handle JavaScript-rendered content")
        print("  This is why Selenium/Playwright is needed for this website")


if __name__ == "__main__":
    print("=" * 70)
    print("Unternehmensregister.de - Working Example with Selenium")
    print("=" * 70)
    print()

    # Show the limitation with requests
    example_simple_requests()

    print("\n" + "=" * 70)
    print("Now trying with Selenium (browser automation)...")
    print("=" * 70)
    print()

    # Try with Selenium
    example_with_selenium()

    print("\n" + "=" * 70)
    print("Summary:")
    print("- requests + BeautifulSoup: Cannot extract data (no JS execution)")
    print("- Selenium/Playwright: Can extract data (full browser)")
    print("- Recommendation: Use Selenium for production use")
    print("=" * 70)
