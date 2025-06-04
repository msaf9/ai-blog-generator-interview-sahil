# seo_fetcher.py

import random

def get_seo_metrics(keyword: str) -> dict:
    """
    Returns mock SEO metrics for the given keyword.
    - search_volume: monthly searches (int)
    - keyword_difficulty: 0-100 scale (int)
    - avg_cpc: average cost-per-click in USD (float)
    """
    # In a real world scenario, you might do an HTTP GET to a free SEO API (e.g., SEMrush, Ahrefs, Ubersuggest).
    # For now, we’ll return consistent but pseudo-random values based on keyword hash.
    seed = abs(hash(keyword)) % (10**8)
    random.seed(seed)

    search_volume = random.randint(1000, 50000)
    keyword_difficulty = random.randint(10, 70)
    avg_cpc = round(random.uniform(0.20, 5.00), 2)

    return {
        "search_volume": search_volume,
        "keyword_difficulty": keyword_difficulty,
        "avg_cpc": avg_cpc
    }
