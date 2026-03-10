import requests

# Test if we can access the markets via their slugs
test_urls = [
    "https://polymarket.com/event/bitboy-convicted",
    "https://polymarket.com/event/russia-ukraine-ceasefire-before-gta-vi-554",
    "https://polymarket.com/event/new-rhianna-album-before-gta-vi-926"
]

for url in test_urls:
    try:
        r = requests.get(url, timeout=10, allow_redirects=True)
        print(f"\n{url}")
        print(f"Status: {r.status_code}")
        print(f"Final URL: {r.url}")
        if r.status_code == 404:
            print("❌ NOT FOUND")
        elif r.status_code == 200:
            print("✅ WORKS")
    except Exception as e:
        print(f"Error: {e}")
