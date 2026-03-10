from utils.api_client import fetch_polymarket_markets, fetch_kalshi_markets

print("Testing Polymarket API...")
pm_markets = fetch_polymarket_markets('All')
print(f"Polymarket returned {len(pm_markets)} markets")
print("\nFirst 3 Polymarket markets:")
for m in pm_markets[:3]:
    print(f"- {m['title'][:80]}")
    print(f"  End date: {m['end_date']}")
    print()

print("\nTesting Kalshi API...")
k_markets = fetch_kalshi_markets('All')
print(f"Kalshi returned {len(k_markets)} markets")
print("\nFirst 3 Kalshi markets:")
for m in k_markets[:3]:
    print(f"- {m['title'][:80]}")
    print(f"  End date: {m['end_date']}")
    print()
