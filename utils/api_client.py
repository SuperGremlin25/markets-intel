import requests
from typing import List, Dict
from datetime import datetime, timezone

POLYMARKET_API_BASE = "https://gamma-api.polymarket.com"
KALSHI_API_BASE = "https://api.elections.kalshi.com/trade-api/v2"

def fetch_polymarket_markets(category: str = "All") -> List[Dict]:
    """
    Fetch markets from Polymarket API
    """
    try:
        markets_url = f"{POLYMARKET_API_BASE}/markets?limit=100&active=true&closed=false"
        response = requests.get(markets_url, timeout=10)
        response.raise_for_status()
        
        all_markets = response.json()
        
        now = datetime.now(timezone.utc)
        active_markets = [
            m for m in all_markets 
            if m.get('active', False) and is_market_current(m.get('endDateIso') or m.get('endDate'), now)
        ]
        
        filtered_markets = []
        for market in active_markets[:100]:
            market_category = categorize_polymarket(market.get('question', ''))
            
            if category == "All" or market_category == category:
                outcome_prices = market.get('outcomePrices', '["0.5", "0.5"]')
                if isinstance(outcome_prices, str):
                    import json
                    outcome_prices = json.loads(outcome_prices)
                
                try:
                    yes_price = float(outcome_prices[0]) if len(outcome_prices) > 0 else 0.5
                    no_price = float(outcome_prices[1]) if len(outcome_prices) > 1 else 0.5
                except (ValueError, TypeError, IndexError):
                    yes_price = 0.5
                    no_price = 0.5
                
                try:
                    volume = float(market.get('volume', 0))
                except (ValueError, TypeError):
                    volume = 0.0
                
                try:
                    liquidity = float(market.get('liquidity', 0))
                except (ValueError, TypeError):
                    liquidity = 0.0
                
                filtered_markets.append({
                    'id': str(market.get('id', '')),
                    'title': market.get('question', 'Unknown'),
                    'platform': 'Polymarket',
                    'category': market_category,
                    'yes_price': yes_price,
                    'no_price': no_price,
                    'volume': volume,
                    'liquidity': liquidity,
                    'end_date': market.get('endDateIso') or market.get('endDate'),
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
        
        now = datetime.now(timezone.utc)
        binary_markets = [
            m for m in all_markets 
            if m.get('market_type') == 'binary' 
            and not m.get('is_provisional', False)
            and is_market_current(m.get('expiration_time'), now)
        ]
        
        filtered_markets = []
        for market in binary_markets[:100]:
            ticker = market.get('market_ticker', market.get('ticker', ''))
            event_ticker = market.get('event_ticker', '')
            
            market_category = categorize_kalshi(event_ticker)
            
            if category == "All" or market_category == category:
                yes_bid = market.get('yes_bid', 50)
                yes_ask = market.get('yes_ask', 50)
                yes_price = (yes_bid + yes_ask) / 2 / 100.0
                
                no_bid = market.get('no_bid', 50)
                no_ask = market.get('no_ask', 50)
                no_price = (no_bid + no_ask) / 2 / 100.0
                
                volume = market.get('volume', 0)
                if isinstance(volume, str):
                    try:
                        volume = float(volume)
                    except ValueError:
                        volume = 0.0
                
                liquidity = market.get('open_interest', 0)
                if isinstance(liquidity, str):
                    try:
                        liquidity = float(liquidity)
                    except ValueError:
                        liquidity = 0.0
                
                title = event_ticker.replace('KX', '').replace('-', ' ').replace('_', ' ')
                if not title:
                    title = ticker
                
                filtered_markets.append({
                    'id': ticker,
                    'title': title,
                    'platform': 'Kalshi',
                    'category': market_category,
                    'yes_price': yes_price,
                    'no_price': no_price,
                    'volume': volume,
                    'liquidity': liquidity,
                    'end_date': market.get('expiration_time'),
                    'url': f"https://kalshi.com/markets/{ticker}"
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
    
    nba_teams = ['lakers', 'warriors', 'celtics', 'heat', 'bucks', 'nets', 'sixers', 'nuggets', 'suns', 'clippers']
    if any(keyword in question_lower for keyword in ['nba'] + nba_teams) and 'basketball' in question_lower:
        return 'NBA'
    elif any(keyword in question_lower for keyword in ['ncaa', 'march madness', 'college basketball', 'duke', 'kentucky', 'kansas']):
        return 'NCAA Basketball'
    elif any(keyword in question_lower for keyword in ['ufc', 'mma', 'fight night', 'fighter', 'mcgregor', 'adesanya']):
        return 'UFC'
    elif any(keyword in question_lower for keyword in ['election', 'president', 'congress', 'senate', 'politics', 'trump', 'biden']):
        return 'World Events'
    else:
        return 'Other'

def categorize_kalshi(title: str) -> str:
    """
    Categorize Kalshi market into sports/events categories
    """
    title_lower = title.lower()
    
    if any(keyword in title_lower for keyword in ['nba', 'ncaamb']):
        if any(keyword in title_lower for keyword in ['ncaa', 'ncaamb', 'college']):
            return 'NCAA Basketball'
        return 'NBA'
    elif any(keyword in title_lower for keyword in ['ncaa', 'march madness', 'college basketball', 'ncaamb']):
        return 'NCAA Basketball'
    elif any(keyword in title_lower for keyword in ['ufc', 'mma', 'fight']):
        return 'UFC'
    elif any(keyword in title_lower for keyword in ['election', 'president', 'congress', 'senate', 'politics']):
        return 'World Events'
    else:
        return 'Other'

def is_market_current(end_date_str: str, now: datetime) -> bool:
    """
    Check if market end date is in the future
    """
    if not end_date_str:
        return True
    
    try:
        if 'T' in end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        else:
            end_date = datetime.fromisoformat(end_date_str).replace(tzinfo=timezone.utc)
        return end_date > now
    except (ValueError, AttributeError, TypeError):
        return True
