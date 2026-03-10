import requests
from typing import List, Dict
from datetime import datetime

POLYMARKET_API_BASE = "https://gamma-api.polymarket.com"
KALSHI_API_BASE = "https://api.elections.kalshi.com/trade-api/v2"

def fetch_polymarket_markets(category: str = "All") -> List[Dict]:
    """
    Fetch markets from Polymarket API
    """
    try:
        markets_url = f"{POLYMARKET_API_BASE}/markets"
        response = requests.get(markets_url, timeout=10)
        response.raise_for_status()
        
        all_markets = response.json()
        
        filtered_markets = []
        for market in all_markets[:50]:
            market_category = categorize_polymarket(market.get('question', ''))
            
            if category == "All" or market_category == category:
                filtered_markets.append({
                    'id': market.get('id'),
                    'title': market.get('question', 'Unknown'),
                    'platform': 'Polymarket',
                    'category': market_category,
                    'yes_price': market.get('outcomePrices', [0.5, 0.5])[0],
                    'no_price': market.get('outcomePrices', [0.5, 0.5])[1],
                    'volume': market.get('volume', 0),
                    'liquidity': market.get('liquidity', 0),
                    'end_date': market.get('endDate'),
                    'url': f"https://polymarket.com/event/{market.get('slug', '')}"
                })
        
        return filtered_markets
    
    except Exception as e:
        print(f"Error fetching Polymarket data: {e}")
        return []

def fetch_kalshi_markets(category: str = "All") -> List[Dict]:
    """
    Fetch markets from Kalshi API
    """
    try:
        markets_url = f"{KALSHI_API_BASE}/markets"
        response = requests.get(markets_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        all_markets = data.get('markets', [])
        
        filtered_markets = []
        for market in all_markets[:50]:
            market_category = categorize_kalshi(market.get('title', ''))
            
            if category == "All" or market_category == category:
                yes_price = market.get('yes_bid', 0.5)
                
                filtered_markets.append({
                    'id': market.get('ticker'),
                    'title': market.get('title', 'Unknown'),
                    'platform': 'Kalshi',
                    'category': market_category,
                    'yes_price': yes_price,
                    'no_price': 1 - yes_price,
                    'volume': market.get('volume', 0),
                    'liquidity': market.get('open_interest', 0),
                    'end_date': market.get('expiration_time'),
                    'url': f"https://kalshi.com/markets/{market.get('ticker', '')}"
                })
        
        return filtered_markets
    
    except Exception as e:
        print(f"Error fetching Kalshi data: {e}")
        return []

def categorize_polymarket(question: str) -> str:
    """
    Categorize Polymarket question into sports/events categories
    """
    question_lower = question.lower()
    
    if any(keyword in question_lower for keyword in ['nba', 'lakers', 'warriors', 'celtics', 'basketball']):
        return 'NBA'
    elif any(keyword in question_lower for keyword in ['ncaa', 'march madness', 'college basketball']):
        return 'NCAA Basketball'
    elif any(keyword in question_lower for keyword in ['ufc', 'mma', 'fight', 'fighter']):
        return 'UFC'
    elif any(keyword in question_lower for keyword in ['election', 'president', 'congress', 'senate', 'politics']):
        return 'World Events'
    else:
        return 'Other'

def categorize_kalshi(title: str) -> str:
    """
    Categorize Kalshi market into sports/events categories
    """
    title_lower = title.lower()
    
    if any(keyword in title_lower for keyword in ['nba', 'basketball']):
        return 'NBA'
    elif any(keyword in title_lower for keyword in ['ncaa', 'march madness', 'college basketball']):
        return 'NCAA Basketball'
    elif any(keyword in title_lower for keyword in ['ufc', 'mma', 'fight']):
        return 'UFC'
    elif any(keyword in title_lower for keyword in ['election', 'president', 'congress', 'senate', 'politics']):
        return 'World Events'
    else:
        return 'Other'
