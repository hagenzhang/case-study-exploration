"""
Comprehensive test suite for the page ID hashing algorithm.

This module tests the compute_page_id function across various scenarios to validate:
1. Stability: Same page produces same ID across different loads
2. Uniqueness: Different pages produce different IDs
3. Robustness: Handles time delays, dynamic content, and page variations
4. Error handling: Gracefully handles invalid URLs

Each test is a standalone async function that can be run independently.
"""

import asyncio
from soup_webpage_id import compute_page_id


# Test URLs loaded from sites.txt
SONGKICK_TOKYO = "https://www.songkick.com/metro-areas/30717-japan-tokyo"
SONGKICK_BARCELONA = "https://www.songkick.com/metro-areas/28714-spain-barcelona"
TICKETMASTER = "https://www.ticketmaster.com/discover/concerts"
EVENTBRITE = "https://www.eventbrite.com/d/spain--barcelona/conferences/"


# ============================================================================
# STABILITY TESTS - Same page should produce same ID
# ============================================================================

async def test_same_page_immediate_reload():
    """
    Test: Load the same page twice in immediate succession.
    
    Significance: This validates that the page ID is deterministic and doesn't
    include volatile elements like timestamps, random ad IDs, or session tokens
    that might change between loads.
    
    Expected: Page IDs should be identical.
    """
    print("\n" + "="*70)
    print("TEST: Same Page - Immediate Reload")
    print("="*70)
    
    page_id_1 = await compute_page_id(SONGKICK_TOKYO)
    page_id_2 = await compute_page_id(SONGKICK_TOKYO)
    
    print(f"First load:  {page_id_1}")
    print(f"Second load: {page_id_2}")
    
    if page_id_1 == page_id_2:
        print("✓ PASS: Page IDs are identical on immediate reload")
        return True
    else:
        print("✗ FAIL: Page IDs differ on immediate reload")
        return False


async def test_same_page_after_delay():
    """
    Test: Load the same page, wait 10 seconds, then load again.
    
    Significance: Real-world pages often have dynamic content that updates
    periodically (ads rotate, "trending" sections change, timestamps update).
    This tests whether our algorithm filters out such volatile content.
    
    Expected: Page IDs should be identical despite time-based content changes.
    """
    print("\n" + "="*70)
    print("TEST: Same Page - After 10 Second Delay")
    print("="*70)
    
    page_id_1 = await compute_page_id(SONGKICK_TOKYO)
    print(f"First load:  {page_id_1}")
    
    print("Waiting 10 seconds...")
    await asyncio.sleep(10)
    
    page_id_2 = await compute_page_id(SONGKICK_TOKYO)
    print(f"Second load: {page_id_2}")
    
    if page_id_1 == page_id_2:
        print("✓ PASS: Page IDs are identical after 10-second delay")
        return True
    else:
        print("✗ FAIL: Page IDs differ after delay (volatile content not filtered)")
        return False


async def test_same_site_different_cities():
    """
    Test: Load two different event listing pages from the same website (Songkick).
    
    Significance: While both pages are from songkick.com and have similar
    structure, they represent different cities (Tokyo vs Barcelona) with
    different events. The algorithm should produce different IDs because the
    core content is different.
    
    Expected: Page IDs should be different.
    """
    print("\n" + "="*70)
    print("TEST: Same Site - Different Cities (Tokyo vs Barcelona)")
    print("="*70)
    
    page_id_tokyo = await compute_page_id(SONGKICK_TOKYO)
    page_id_barcelona = await compute_page_id(SONGKICK_BARCELONA)
    
    print(f"Tokyo:     {page_id_tokyo}")
    print(f"Barcelona: {page_id_barcelona}")
    
    if page_id_tokyo != page_id_barcelona:
        print("✓ PASS: Different cities produce different page IDs")
        return True
    else:
        print("✗ FAIL: Different cities produce same page ID (algorithm too aggressive)")
        return False


# ============================================================================
# UNIQUENESS TESTS - Different pages should produce different IDs
# ============================================================================

async def test_different_sites_all_unique():
    """
    Test: Load all four different sites and verify each produces a unique ID.
    
    Significance: This validates that the algorithm can distinguish between
    completely different websites with different structures, content, and
    purposes. Each site (Songkick, Ticketmaster, Eventbrite) has its own
    unique layout and event data.
    
    Expected: All four page IDs should be unique.
    """
    print("\n" + "="*70)
    print("TEST: Different Sites - All Should Be Unique")
    print("="*70)
    
    urls = [SONGKICK_TOKYO, SONGKICK_BARCELONA, TICKETMASTER, EVENTBRITE]
    page_ids = {}
    
    for url in urls:
        page_id = await compute_page_id(url)
        page_ids[url] = page_id
        print(f"{url[:50]:50} -> {page_id}")
    
    unique_ids = set(page_ids.values())
    
    if None in unique_ids:
        print("✗ FAIL: One or more URLs failed to load")
        return False
    
    if len(unique_ids) == len(urls):
        print(f"✓ PASS: All {len(urls)} sites produce unique page IDs")
        return True
    else:
        print(f"✗ FAIL: Only {len(unique_ids)} unique IDs from {len(urls)} sites")
        return False


async def test_cross_site_comparison():
    """
    Test: Load Ticketmaster and Eventbrite and verify they have different IDs.
    
    Significance: Both sites serve similar purposes (event discovery) and might
    have similar structural elements (search bars, event listings, filters).
    This tests whether the algorithm can distinguish between sites with similar
    purposes but different implementations.
    
    Expected: Page IDs should be different.
    """
    print("\n" + "="*70)
    print("TEST: Cross-Site Comparison (Ticketmaster vs Eventbrite)")
    print("="*70)
    
    page_id_tm = await compute_page_id(TICKETMASTER)
    page_id_eb = await compute_page_id(EVENTBRITE)
    
    print(f"Ticketmaster: {page_id_tm}")
    print(f"Eventbrite:   {page_id_eb}")
    
    if page_id_tm != page_id_eb:
        print("✓ PASS: Different sites produce different page IDs")
        return True
    else:
        print("✗ FAIL: Different sites produce same page ID")
        return False


# ============================================================================
# ROBUSTNESS TESTS - Algorithm should handle edge cases
# ============================================================================

async def test_sequential_loads_stability():
    """
    Test: Load the same page 5 times in rapid succession.
    
    Significance: This stress-tests the stability of the algorithm. In a
    real crawler, you might revisit the same page multiple times. Each load
    might get slightly different ad content, cookie banners, or dynamic elements.
    The core page ID should remain stable.
    
    Expected: All 5 loads should produce identical page IDs.
    """
    print("\n" + "="*70)
    print("TEST: Sequential Loads - 5 Rapid Reloads of Same Page")
    print("="*70)
    
    page_ids = []
    for i in range(5):
        page_id = await compute_page_id(SONGKICK_TOKYO)
        page_ids.append(page_id)
        print(f"Load {i+1}: {page_id}")
    
    unique_ids = set(page_ids)
    
    if len(unique_ids) == 1:
        print("✓ PASS: All 5 loads produced identical page IDs")
        return True
    else:
        print(f"✗ FAIL: Got {len(unique_ids)} different IDs from 5 loads")
        return False


async def test_navigation_path_affects_id():
    """
    Test: Load the same page with different navigation paths.
    
    Significance: The compute_page_id function includes nav_path in its hash.
    This tests that different navigation paths to the same page produce
    different IDs, which is important for tracking how users discovered content.
    
    Expected: Different nav_paths should produce different page IDs.
    """
    print("\n" + "="*70)
    print("TEST: Navigation Path - Same Page, Different Paths")
    print("="*70)
    
    page_id_root = await compute_page_id(SONGKICK_TOKYO, nav_path=["root"])
    page_id_search = await compute_page_id(SONGKICK_TOKYO, nav_path=["home", "search", "tokyo"])
    page_id_direct = await compute_page_id(SONGKICK_TOKYO, nav_path=["direct_link"])
    
    print(f"Path ['root']:                  {page_id_root}")
    print(f"Path ['home','search','tokyo']: {page_id_search}")
    print(f"Path ['direct_link']:           {page_id_direct}")
    
    unique_ids = {page_id_root, page_id_search, page_id_direct}
    
    if len(unique_ids) == 3:
        print("✓ PASS: Different navigation paths produce different page IDs")
        return True
    else:
        print("✗ FAIL: Navigation path not properly affecting page ID")
        return False


# ============================================================================
# ERROR HANDLING TESTS - Algorithm should gracefully handle failures
# ============================================================================

async def test_invalid_url():
    """
    Test: Attempt to compute page ID for an invalid URL.
    
    Significance: Real-world crawlers will encounter broken links, typos, and
    malformed URLs. The algorithm should handle these gracefully by returning
    None rather than crashing.
    
    Expected: Should return None and not raise an exception.
    """
    print("\n" + "="*70)
    print("TEST: Error Handling - Invalid URL")
    print("="*70)
    
    invalid_urls = [
        "not-a-valid-url",
        "htp://missing-letter.com",
        "https://",
        "https://this-domain-definitely-does-not-exist-12345.com"
    ]
    
    all_handled = True
    for url in invalid_urls:
        try:
            page_id = await compute_page_id(url)
            if page_id is None:
                print(f"✓ Correctly returned None for: {url}")
            else:
                print(f"✗ Unexpectedly got ID for invalid URL: {url}")
                all_handled = False
        except Exception as e:
            print(f"✗ Exception raised for {url}: {e}")
            all_handled = False
    
    if all_handled:
        print("✓ PASS: All invalid URLs handled gracefully")
        return True
    else:
        print("✗ FAIL: Some invalid URLs not handled properly")
        return False


# ============================================================================
# COMPREHENSIVE TEST RUNNER
# ============================================================================

async def run_all_tests():
    """
    Run all test cases and provide a summary report.
    
    This function executes all tests and tracks pass/fail status.
    """
    print("\n" + "="*70)
    print("RUNNING COMPREHENSIVE PAGE HASHER TEST SUITE")
    print("="*70)
    
    tests = [
        ("Same Page - Immediate Reload", test_same_page_immediate_reload),
        ("Same Page - After Delay", test_same_page_after_delay),
        ("Same Site - Different Cities", test_same_site_different_cities),
        ("Different Sites - All Unique", test_different_sites_all_unique),
        ("Cross-Site Comparison", test_cross_site_comparison),
        ("Sequential Loads Stability", test_sequential_loads_stability),
        ("Navigation Path Affects ID", test_navigation_path_affects_id),
        ("Invalid URL Handling", test_invalid_url),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            passed = await test_func()
            results[test_name] = passed
        except Exception as e:
            print(f"\n✗ EXCEPTION in {test_name}: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✓ PASS" if passed_flag else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("="*70)
    print(f"OVERALL: {passed}/{total} tests passed ({100*passed//total}%)")
    print("="*70)


# ============================================================================
# INDIVIDUAL TEST RUNNERS
# ============================================================================

async def run_stability_tests():
    """Run only stability-related tests."""
    print("\n=== STABILITY TESTS ===")
    await test_same_page_immediate_reload()
    await test_same_page_after_delay()
    await test_sequential_loads_stability()


async def run_uniqueness_tests():
    """Run only uniqueness-related tests."""
    print("\n=== UNIQUENESS TESTS ===")
    await test_same_site_different_cities()
    await test_different_sites_all_unique()
    await test_cross_site_comparison()


async def run_robustness_tests():
    """Run only robustness and error handling tests."""
    print("\n=== ROBUSTNESS TESTS ===")
    await test_navigation_path_affects_id()
    await test_invalid_url()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Allow running specific tests from command line
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        
        test_map = {
            "immediate": test_same_page_immediate_reload,
            "delay": test_same_page_after_delay,
            "cities": test_same_site_different_cities,
            "unique": test_different_sites_all_unique,
            "crosssite": test_cross_site_comparison,
            "sequential": test_sequential_loads_stability,
            "navpath": test_navigation_path_affects_id,
            "invalid": test_invalid_url,
            "stability": run_stability_tests,
            "uniqueness": run_uniqueness_tests,
            "robustness": run_robustness_tests,
        }
        
        if test_name in test_map:
            print(f"Running specific test: {test_name}")
            asyncio.run(test_map[test_name]())
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available tests: {', '.join(test_map.keys())}")
    else:
        # Run all tests by default
        asyncio.run(run_all_tests())

