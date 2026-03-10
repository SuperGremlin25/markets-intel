import requests

# Get a market we know works
r = requests.get('https://gamma-api.polymarket.com/markets?limit=100&active=true&closed=false', timeout=10)
markets = r.json()

# Find the BitBoy market that worked
for m in markets:
    if 'bitboy' in m.get('question', '').lower():
        print("BitBoy market (WORKING):")
        print(f"Question: {m.get('question')}")
        print(f"Slug: {m.get('slug')}")
        print(f"ID: {m.get('id')}")
        print(f"Condition ID: {m.get('conditionId')}")
        print(f"\nAll URL-related fields:")
        for key in m.keys():
            if any(x in key.lower() for x in ['url', 'slug', 'link', 'id', 'condition']):
                print(f"  {key}: {m.get(key)}")
        break

print("\n" + "="*50)
print("\nRussia-Ukraine market (NOT WORKING):")
for m in markets:
    if 'russia-ukraine' in m.get('slug', '').lower():
        print(f"Question: {m.get('question')}")
        print(f"Slug: {m.get('slug')}")
        print(f"ID: {m.get('id')}")
        print(f"Condition ID: {m.get('conditionId')}")
        print(f"\nAll URL-related fields:")
        for key in m.keys():
            if any(x in key.lower() for x in ['url', 'slug', 'link', 'id', 'condition']):
                print(f"  {key}: {m.get(key)}")
        break
