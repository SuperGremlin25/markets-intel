from typing import List, Dict
import pandas as pd

def normalize_market_data(polymarket_data: List[Dict], kalshi_data: List[Dict]) -> List[Dict]:
    """
    Combine and normalize data from both platforms
    """
    all_markets = polymarket_data + kalshi_data
    
    all_markets.sort(key=lambda x: x.get('volume', 0), reverse=True)
    
    return all_markets

def calculate_arbitrage(markets: List[Dict], min_profit: float = 0.02) -> List[Dict]:
    """
    Find arbitrage opportunities between Polymarket and Kalshi
    """
    arbitrage_opportunities = []
    
    polymarket_markets = {m['title']: m for m in markets if m['platform'] == 'Polymarket'}
    kalshi_markets = {m['title']: m for m in markets if m['platform'] == 'Kalshi'}
    
    for title in polymarket_markets:
        if title in kalshi_markets:
            poly_market = polymarket_markets[title]
            kalshi_market = kalshi_markets[title]
            
            poly_yes = poly_market['yes_price']
            kalshi_yes = kalshi_market['yes_price']
            
            profit_poly_to_kalshi = kalshi_yes - poly_yes
            profit_kalshi_to_poly = poly_yes - kalshi_yes
            
            if profit_poly_to_kalshi > min_profit:
                arbitrage_opportunities.append({
                    'title': title,
                    'platform_1': 'Polymarket',
                    'price_1': poly_yes,
                    'platform_2': 'Kalshi',
                    'price_2': kalshi_yes,
                    'profit': profit_poly_to_kalshi,
                    'direction': 'Buy Polymarket, Sell Kalshi'
                })
            
            elif profit_kalshi_to_poly > min_profit:
                arbitrage_opportunities.append({
                    'title': title,
                    'platform_1': 'Kalshi',
                    'price_1': kalshi_yes,
                    'platform_2': 'Polymarket',
                    'price_2': poly_yes,
                    'profit': profit_kalshi_to_poly,
                    'direction': 'Buy Kalshi, Sell Polymarket'
                })
    
    arbitrage_opportunities.sort(key=lambda x: x['profit'], reverse=True)
    
    return arbitrage_opportunities

def calculate_market_sentiment(markets: List[Dict]) -> Dict:
    """
    Calculate overall market sentiment metrics
    """
    if not markets:
        return {}
    
    df = pd.DataFrame(markets)
    
    sentiment = {
        'total_markets': len(markets),
        'avg_yes_price': df['yes_price'].mean(),
        'total_volume': df['volume'].sum(),
        'total_liquidity': df['liquidity'].sum(),
        'by_category': df.groupby('category').agg({
            'yes_price': 'mean',
            'volume': 'sum'
        }).to_dict()
    }
    
    return sentiment

def filter_markets_by_date(markets: List[Dict], days_ahead: int = 30) -> List[Dict]:
    """
    Filter markets by end date
    """
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() + timedelta(days=days_ahead)
    
    filtered = []
    for market in markets:
        if market.get('end_date'):
            try:
                end_date = datetime.fromisoformat(market['end_date'].replace('Z', '+00:00'))
                if end_date <= cutoff_date:
                    filtered.append(market)
            except:
                filtered.append(market)
        else:
            filtered.append(market)
    
    return filtered
