import hashlib
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def compute_page_id(url: str, nav_path=None):
    """
    Compute a stable, noise-resistant ID for the current logical page.
    Works even for SPAs and pages with dynamic ads or content.
    
    Args:
        url: The URL string to load and compute the page ID for
        nav_path: Optional list of navigation steps (defaults to ["root"])
    
    Returns:
        A SHA-1 hash string representing the page ID, or None if an error occurs
    """
    if nav_path is None:
        nav_path = ["root"]
    
    browser = None
    try:
        # Launch browser and navigate to the URL
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Navigate to URL with timeout
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Gather key info
            actual_url = page.url
            html = await page.content()
            
            await browser.close()
        
        # Parse DOM with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Remove volatile tags
        for tag in soup(["script", "style", "iframe", "noscript"]):
            tag.decompose()

        # Remove obvious dynamic elements (ads, tracking, etc.)
        for selector in [".ads", ".sponsored", "[id*=ad]", "[class*=ad]"]:
            for el in soup.select(selector):
                el.decompose()

        # Extract stable metadata
        title = (soup.title.string.strip() if soup.title else "")
        canonical = soup.find("link", rel="canonical")
        canonical_url = canonical["href"].strip() if canonical and canonical.get("href") else None

        # Fallback to current page URL if no canonical tag
        canonical_url = canonical_url or actual_url.split("#")[0]

        # Compute structural signature
        # Get sequence of HTML tag names in order (ignoring text)
        tags = [tag.name for tag in soup.find_all()]
        structure_fingerprint = hashlib.sha1(" ".join(tags).encode()).hexdigest()

        # Extract main header or og:title if available
        og_title = soup.find("meta", property="og:title")
        main_header = ""
        if og_title and og_title.get("content"):
            main_header = og_title["content"].strip()
        else:
            h1 = soup.find("h1")
            if h1:
                main_header = re.sub(r"\s+", " ", h1.get_text().strip())

        # Combine everything into a normalized identity tuple
        identity_tuple = (
            canonical_url,
            title.lower(),
            main_header.lower(),
            structure_fingerprint,
            " -> ".join(nav_path),
        )

        # Compute stable hash of all combined data
        combined = "|".join(identity_tuple)
        page_id = hashlib.sha1(combined.encode("utf-8")).hexdigest()

        return page_id
    
    except Exception as e:
        # Handle any errors (invalid URL, network issues, timeout, etc.)
        print(f"[ERROR] Failed to compute page ID for {url}: {e}")
        if browser:
            try:
                await browser.close()
            except:
                pass
        return None