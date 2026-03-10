import requests

r = requests.get('https://gamma-api.polymarket.com/markets?limit=5&active=true&closed=false', timeout=10)
markets = r.json()

print("Checking Polymarket URL structure:\n")
for m in markets[:3]:
    print(f"Question: {m.get('question')}")
    print(f"Slug: {m.get('slug')}")
    print(f"ID: {m.get('id')}")
    print(f"Constructed URL: https://polymarket.com/event/{m.get('slug')}")
    print()
