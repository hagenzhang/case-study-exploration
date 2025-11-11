import argparse
import hashlib
import os
import re
import sys
from html import unescape


def extract_readable_text(html_content: str) -> str:
    """Extract visible, human-readable text from raw HTML.

    Heuristics:
    - Strip <script> and <style> blocks and their contents
    - Remove HTML comments
    - Remove all remaining tags
    - Decode HTML entities
    - Collapse whitespace
    """
    # Remove script and style contents
    without_script = re.sub(r"<script[\s\S]*?</script>", " ", html_content, flags=re.IGNORECASE)
    without_style = re.sub(r"<style[\s\S]*?</style>", " ", without_script, flags=re.IGNORECASE)

    # Remove HTML comments
    without_comments = re.sub(r"<!--([\s\S]*?)-->", " ", without_style)

    # Remove all remaining tags
    without_tags = re.sub(r"<[^>]+>", " ", without_comments)

    # Decode HTML entities (e.g., &amp; -> &)
    decoded = unescape(without_tags)

    # Normalize and collapse whitespace
    collapsed = re.sub(r"\s+", " ", decoded).strip()
    return collapsed


def normalize_text_for_hash(text: str) -> str:
    """Normalize text to improve robustness of the signature.

    - Lowercase via casefold for better unicode handling
    - Remove non-essential punctuation that often varies
    - Collapse whitespace (already mostly collapsed, but enforce again)
    """
    lower = text.casefold()
    # Keep letters, numbers, and whitespace; drop most punctuation
    kept = re.sub(r"[^\w\s]", "", lower, flags=re.UNICODE)
    normalized = re.sub(r"\s+", " ", kept).strip()
    return normalized


def compute_dom_signature_from_readable(html_content: str) -> str:
    """Compute a stable signature using only the readable content of the DOM."""
    readable = extract_readable_text(html_content)
    normalized = normalize_text_for_hash(readable)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute DOM content signatures from two HTML text files and compare them.")
    parser.add_argument("file1", help="Path to first .txt file containing HTML")
    parser.add_argument("file2", help="Path to second .txt file containing HTML")
    args = parser.parse_args()

    if not os.path.exists(args.file1):
        print(f"[ERROR] File not found: {args.file1}")
        sys.exit(1)
    if not os.path.exists(args.file2):
        print(f"[ERROR] File not found: {args.file2}")
        sys.exit(1)

    html1 = read_text_file(args.file1)
    html2 = read_text_file(args.file2)

    sig1 = compute_dom_signature_from_readable(html1)
    sig2 = compute_dom_signature_from_readable(html2)

    are_same = sig1 == sig2

    print("First file signature:", sig1)
    print("Second file signature:", sig2)
    print("Same page by readable-content signature:", "YES" if are_same else "NO")


if __name__ == "__main__":
    main()


