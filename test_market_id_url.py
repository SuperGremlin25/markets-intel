import requests

# Get market data
r = requests.get('https://gamma-api.polymarket.com/markets?limit=5&active=true&closed=false', timeout=10)
markets = r.json()

# Test different URL patterns
for m in markets[:3]:
    question = m.get('question')[:50]
    market_id = m.get('id')
    slug = m.get('slug')
    condition_id = m.get('conditionId')
    
    print(f"\n{question}...")
    print(f"Market ID: {market_id}")
    print(f"Slug: {slug}")
    
    # Test different URL patterns
    test_urls = [
        f"https://polymarket.com/event/{slug}",
        f"https://polymarket.com/market/{slug}",
        f"https://polymarket.com/markets/{market_id}",
        f"https://polymarket.com/event?id={market_id}"
    ]
    
    for url in test_urls:
        try:
            resp = requests.head(url, timeout=5, allow_redirects=True)
            if resp.status_code == 200:
                print(f"  ✅ WORKS: {url}")
                break
        except:
            pass
    else:
        print(f"  ❌ No working URL found")
