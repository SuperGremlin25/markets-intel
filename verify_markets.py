import requests

# Get markets from API
r = requests.get('https://gamma-api.polymarket.com/markets?limit=10&active=true&closed=false', timeout=10)
markets = r.json()

print("Verifying first 10 markets from Polymarket API:\n")
for i, m in enumerate(markets[:10], 1):
    question = m.get('question', 'Unknown')
    slug = m.get('slug', '')
    url = f"https://polymarket.com/event/{slug}"
    active = m.get('active')
    closed = m.get('closed')
    end_date = m.get('endDateIso') or m.get('endDate')
    
    print(f"{i}. {question[:60]}")
    print(f"   URL: {url}")
    print(f"   Active: {active}, Closed: {closed}, End: {end_date}")
    print()
