from playwright.async_api import async_playwright
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()
browser_instance_dir = os.environ.get('BROWSER_INSTANCE_DIR')
user_data_dir = os.environ.get('USER_DATA_DIR')
downloads_dir = os.environ.get('DOWNLOADS_DIR')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto('https://google.com')
        await page.wait_for_load_state('load')
        await asyncio.sleep(5)
        # Inject JavaScript and execute functions
        elements = await page.evaluate("""
            (async () => {
                async function loadAllCSSInStyle() {
                    const stylesheets = document.styleSheets;
                    let allCSS = ""; // Store all CSS content
                    
                    let fetchPromises = Array.from(stylesheets).map(async (stylesheet) => {
                        if (stylesheet.href) {
                            try {
                                let response = await fetch(stylesheet.href);
                                if (response.ok) {
                                    let text = await response.text();
                                    allCSS += `\\n/* ${stylesheet.href} */\\n` + text; // Append fetched CSS
                                }
                            } catch (error) {
                                console.error('Error fetching CSS:', stylesheet.href, error);
                            }
                        }
                    });

                    // Wait for all fetches to complete
                    await Promise.all(fetchPromises);

                    // Inject into a single <style> tag
                    if (allCSS.trim()) {
                        const styleElement = document.createElement('style');
                        styleElement.textContent = allCSS;
                        document.head.appendChild(styleElement);
                    }
                }

                await loadAllCSSInStyle();  // Ensure styles are loaded before checking
                
                function getInteractiveClassesFromInjectedCSS() {
                    const interactiveClasses = new Set();

                    for (const sheet of document.styleSheets) {
                        try {
                            for (const rule of sheet.cssRules) {
                                if (!rule.selectorText) continue;

                                // Check for cursor styles or pseudo-classes
                                if (
                                    rule.cssText.includes("cursor:") ||
                                    rule.selectorText.includes(":hover") ||
                                    rule.selectorText.includes(":focus") ||
                                    rule.selectorText.includes(":active") ||
                                    rule.cssText.includes("animation") ||
                                    rule.cssText.includes("transition")
                                ) {
                                    const classes = rule.selectorText.match(/\\.[\\w-]+/g); // Extract class names
                                    if (classes) {
                                        classes.forEach(cls => interactiveClasses.add(cls.replace(".", ""))); // Store without '.'
                                    }
                                }
                            }
                        } catch (e) {
                            console.warn("Couldn't access stylesheet:", sheet.href);
                        }
                    }

                    return [...interactiveClasses];
                }

                return getInteractiveClassesFromInjectedCSS();
            })(); // Immediately Invoked Function Expression (IIFE)
        """)

        print("Elements:", elements)
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
