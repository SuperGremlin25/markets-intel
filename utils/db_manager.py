"""
Database manager for Markets Intel
Handles Supabase integration and data persistence
"""

import os
from datetime import datetime
from typing import List, Dict, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        self.client = None
        self.enabled = False
        
        if supabase_url and supabase_key and supabase_key != 'your_anon_key_here':
            try:
                # Create client with minimal options to avoid compatibility issues
                from supabase import create_client as supabase_create_client
                self.client = supabase_create_client(
                    supabase_url=supabase_url,
                    supabase_key=supabase_key
                )
                self.enabled = True
                print("✅ Supabase connected successfully")
            except Exception as e:
                print(f"⚠️ Supabase connection failed: {str(e)}")
                print("Database features disabled. App will continue without historical data.")
                self.client = None
                self.enabled = False
        else:
            print("⚠️ Supabase credentials not configured. Database features disabled.")
    
    def store_market_snapshot(self, market: Dict) -> bool:
        """Store a market snapshot for historical tracking"""
        if not self.enabled:
            return False
        
        try:
            data = {
                'market_id': market['id'],
                'platform': market['platform'],
                'title': market['title'],
                'category': market['category'],
                'yes_price': market['yes_price'],
                'no_price': market['no_price'],
                'volume': market.get('volume', 0),
                'liquidity': market.get('liquidity', 0),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.client.table('market_snapshots').insert(data).execute()
            return True
        except Exception as e:
            print(f"Error storing market snapshot: {e}")
            return False
    
    def get_market_history(self, market_id: str, hours: int = 24) -> List[Dict]:
        """Get historical data for a specific market"""
        if not self.enabled:
            return []
        
        try:
            from datetime import timedelta
            cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
            
            response = self.client.table('market_snapshots')\
                .select('*')\
                .eq('market_id', market_id)\
                .gte('timestamp', cutoff)\
                .order('timestamp')\
                .execute()
            
            return response.data
        except Exception as e:
            print(f"Error fetching market history: {e}")
            return []
    
    def get_24hr_price_change(self, market_id: str) -> Optional[float]:
        """Calculate 24-hour price change for a market"""
        history = self.get_market_history(market_id, hours=24)
        
        if len(history) < 2:
            return None
        
        old_price = history[0]['yes_price']
        new_price = history[-1]['yes_price']
        
        return new_price - old_price
    
    def store_user_subscription(self, user_data: Dict) -> bool:
        """Store user subscription data"""
        if not self.enabled:
            return False
        
        try:
            self.client.table('subscriptions').insert(user_data).execute()
            return True
        except Exception as e:
            print(f"Error storing subscription: {e}")
            return False
    
    def get_user_subscription(self, discord_id: str) -> Optional[Dict]:
        """Get user subscription status"""
        if not self.enabled:
            return None
        
        try:
            response = self.client.table('subscriptions')\
                .select('*')\
                .eq('discord_id', discord_id)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching subscription: {e}")
            return None

# Global database instance
db = DatabaseManager()
