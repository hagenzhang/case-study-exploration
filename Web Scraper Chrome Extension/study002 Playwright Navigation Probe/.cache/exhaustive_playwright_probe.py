"""
We need to now implement a LLM to check if a site has multiple events on the page to see if it is a worthwhile
page to save.

If it is a single event page or has no events, just skip it.

Maybe we can take the DOM and then utilize word embeddings to see if the page is a worthwhile page to save? Like
we can make a threshold, and potentially train a model to determine if the page has multiple events on the page.
"""

# filtered_playwright_probe_logging.py
# Async Playwright crawler that explores a site to a limited depth, captures
# actions taken (scrolls and clicks), and writes a structured JSON log.
import asyncio
import hashlib
import json
from playwright.async_api import async_playwright

MAX_DEPTH = 1  # Limit how many actions from the root we perform before stopping
UNWANTED_TEXT_KEYWORDS = ["login", "signup", "help", "contact", "language", "terms", "privacy"]  # Heuristic filters for non-content links
UNWANTED_URL_SUBSTRINGS = ["/account", "/help", "/language", "/terms", "/privacy"]  # URL-based filters for nav/legal pages
VISITED = {}  # Map of DOM signature to a record of the URL and action path used to reach it

# ---------------- Helper functions ---------------- #

def compute_dom_signature(html: str) -> str:
    """Create a stable signature of the DOM to identify pages we've seen.

    Using a hash of the full HTML allows us to de-duplicate pages reached by
    different action paths but rendering the same content.
    """
    return hashlib.sha256(html.encode("utf-8")).hexdigest()


def append_action(path, action):
    """Return a new action path with the additional action appended."""
    return path + [action]


def is_unwanted(text: str, url: str) -> bool:
    """Heuristic check to skip navigational or irrelevant elements.

    Filters based on visible text and URL fragments to avoid logins, legal,
    language-switchers, and similar non-target actions.
    """
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in UNWANTED_TEXT_KEYWORDS):
        return True
    url_lower = (url or "").lower()
    if any(substr in url_lower for substr in UNWANTED_URL_SUBSTRINGS):
        return True
    return False

# ---------------- Probe function ---------------- #

async def run_probe(root_url: str):
    """Visit the root URL and explore clickable elements up to MAX_DEPTH.

    For each unique DOM encountered, we track the sequence of actions required
    to reach it. Actions include scrolls and clicks.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Run without opening a visible browser window
        context = await browser.new_context()  # Isolate cookies/storage per run
        page = await context.new_page()  # Single tab used for exploration

        # Queue as set: each item is (url, hashable_actions_string)
        queue = set()  # A set avoids duplicates; items are (url, actions_json)
        queue.add((root_url, "[]"))  # Seed with the root and an empty action list
        depth_map = {}  # Tracks the shortest known depth for a given dom_signature

        while queue:
            url, actions_json = queue.pop()
            actions_from_root = json.loads(actions_json)  # Materialize the action list
            depth = len(actions_from_root)
            if depth > MAX_DEPTH:
                print(f"[SKIP] Max depth reached for {url}")
                continue

            try:
                print(f"[VISIT] URL: {url} | Depth: {depth} | Actions: {len(actions_from_root)}")
                await page.goto(url, wait_until="domcontentloaded")  # Navigate and wait for DOM ready
                html = await page.content()  # Snapshot of rendered DOM
                dom_signature = compute_dom_signature(html)  # Unique key for current content

                # Skip if already visited with shorter path
                if dom_signature in VISITED and len(VISITED[dom_signature]["actions"]) <= len(actions_from_root):
                    print(f"[SKIP] Already visited (shorter path exists) {url}")
                    continue

                # Record this page and how we got here
                VISITED[dom_signature] = {"url": url, "actions": list(actions_from_root)}
                print(f"[SAVE] Stored page {url} | Actions: {len(actions_from_root)}")

                # Scroll to bottom to load lazy content
                # Compute total scroll height to force lazy-loaded content to render
                scroll_height = await page.evaluate("() => document.body.scrollHeight")
                if scroll_height > 0:
                    # Represent a scroll action and schedule revisiting the same URL with it applied
                    new_actions = append_action(list(actions_from_root), {"scroll": {"y": scroll_height}})
                    new_actions_json = json.dumps(new_actions)
                    new_dom_sig = compute_dom_signature(html + new_actions_json)
                    if new_dom_sig not in depth_map or depth_map[new_dom_sig] > depth + 1:
                        queue.add((url, new_actions_json))
                        depth_map[new_dom_sig] = depth + 1
                        print(f"[QUEUE] Added scroll action for {url}")

                # Find clickable elements
                # Collect candidate clickable elements (links and buttons)
                clickable_elements = await page.query_selector_all("a, button")
                for el in clickable_elements:
                    # Skip elements not visible to the user
                    visible = await el.is_visible()
                    if not visible:
                        continue

                    # Gather basic metadata for filtering & logging
                    inner_text = await el.inner_text()
                    href_attr = await el.get_attribute("href")
                    href = href_attr if href_attr else ""
                    if is_unwanted(inner_text, href):
                        print(f"[SKIP] Ignored element with text '{inner_text}' or URL '{href}'")
                        continue

                    # Build a stable selector and capture the class for the output log
                    tag_name = await el.evaluate("(e) => e.tagName")
                    class_attr = await el.get_attribute("class") or ""
                    if tag_name == "A":
                        selector = f'a[href="{href}"]'
                    else:
                        selector = await el.evaluate(
                            "(e) => e.tagName + ':nth-of-type(' + (Array.from(e.parentNode.children).indexOf(e)+1) + ')'"
                        )

                    # Represent the click with selector and class metadata, then schedule it
                    new_actions = append_action(list(actions_from_root), {"click": {"selector": selector, "class": class_attr}})
                    new_actions_json = json.dumps(new_actions)
                    new_dom_sig = compute_dom_signature(html + new_actions_json)
                    if new_dom_sig not in depth_map or depth_map[new_dom_sig] > depth + 1:
                        queue.add((url, new_actions_json))
                        depth_map[new_dom_sig] = depth + 1

            except Exception as e:
                print(f"[ERROR] Visiting {url}: {e}")
                continue

        # Cleanly shutdown browser resources
        await browser.close()
        return VISITED

# ---------------- Main ---------------- #

async def main():
    """Entrypoint; configure the root URL, run the probe, and write results."""
    root_url = "https://www.songkick.com/metro-areas/30717-japan-tokyo"
    visited_pages = await run_probe(root_url)

    # Normalize the map into a list for JSON output
    output = []
    for v in visited_pages.values():
        output.append({
            "url": v["url"],
            "actions": v["actions"],
            "dom_signature": compute_dom_signature(v["url"])
        })

    # Persist results in a stable, readable JSON structure
    with open("filtered_probe_logging_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("Probe complete. Output saved to filtered_probe_logging_output.json")


if __name__ == "__main__":
    asyncio.run(main())
