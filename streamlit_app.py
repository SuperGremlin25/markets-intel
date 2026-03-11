import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from utils.api_client import fetch_polymarket_markets
from utils.data_processor import normalize_market_data, calculate_arbitrage
from utils.visualizations import create_odds_chart, create_network_map
from utils.db_manager import db
import config

st.set_page_config(
    page_title="Markets Intel - AI-Powered Prediction Market Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark terminal theme
st.markdown("""
<style>
    .main {
        background-color: #06060a;
    }
    .stMetric {
        background-color: #0f0f14;
        padding: 10px;
        border-radius: 5px;
    }
    h1, h2, h3 {
        color: #00ff88;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎯 Markets Intel")
st.markdown("**AI-Powered Prediction Market Intelligence**")
st.markdown("Real-time data • Social sentiment • Arbitrage detection • Whale tracking")

with st.sidebar:
    st.header("⚙️ View Options")
    
    view_mode = st.selectbox(
        "Sort By",
        ["Most Active", "Biggest Movers", "All Markets"]
    )
    
    st.markdown("**Platform:** Polymarket")
    st.caption("Kalshi integration removed due to data quality issues")
    
    st.markdown("---")
    st.markdown("### � Upgrade")
    st.markdown("**Premium** ($29/mo)")
    st.markdown("• AI predictions")
    st.markdown("• Real-time whale alerts")
    st.markdown("• Arbitrage opportunities")
    
    st.markdown("**Pro** ($99/mo)")
    st.markdown("• Everything in Premium")
    st.markdown("• Auto-execution guidance")
    st.markdown("• Portfolio optimizer")
    
    st.link_button("Upgrade Now", "https://digital-insurgent-media.com/markets", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🎮 Join Community")
    st.markdown("[Discord Server](https://discord.gg/your-invite)")
    st.markdown("Get alerts, discuss markets, share wins")
    
    st.markdown("---")
    st.markdown("### 🔗 Trade on Polymarket")
    st.markdown("[Sign up for Polymarket](https://polymarket.com)")
    st.markdown("*Affiliate link - we may earn commission*")

def load_market_data(view_mode):
    # Only fetch Polymarket data (Kalshi removed due to data quality issues)
    polymarket_data = fetch_polymarket_markets('All')
    combined_data = polymarket_data
    
    # Add 24hr price changes
    for market in combined_data:
        change = db.get_24hr_price_change(market['id'])
        market['change_24hr'] = change if change is not None else 0
    
    # Sort based on view mode
    if view_mode == "Most Active":
        combined_data.sort(key=lambda x: x.get('volume', 0), reverse=True)
    elif view_mode == "Biggest Movers":
        combined_data.sort(key=lambda x: abs(x.get('change_24hr', 0)), reverse=True)
    
    return combined_data

with st.spinner("Loading market data..."):
    markets = load_market_data(view_mode)
    
    # Store snapshots for historical tracking
    for market in markets[:50]:  # Store top 50 markets
        db.store_market_snapshot(market)

tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Odds", "📈 Historical Trends", "🕸️ Network Analysis", "💎 Arbitrage"])

with tab1:
    st.header("Live Market Odds")
    
    if markets:
        st.success(f"Found {len(markets)} active markets")
        
        for idx, market in enumerate(markets):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{market['title']}**")
                st.caption(f"{market['platform']} • {market['category']}")
            
            with col2:
                st.metric("Yes", f"${market['yes_price']:.2f}")
            
            with col3:
                st.metric("No", f"${market['no_price']:.2f}")
            
            with col4:
                st.link_button("View Market", market['url'], use_container_width=True)
            
            st.markdown("---")
    else:
        st.info("No markets found for selected filters")

with tab2:
    st.header("📈 Historical Price Trends")
    st.info("Historical data visualization - Coming soon in Phase 2")
    st.markdown("Track how market odds change over time")

with tab3:
    st.header("🕸️ Market Correlation Network")
    st.info("Network analysis - Coming soon in Phase 2")
    st.markdown("Visualize how different markets influence each other")

with tab4:
    st.header("💎 Arbitrage Opportunities")
    
    arbitrage_opps = calculate_arbitrage(markets)
    
    if arbitrage_opps:
        st.success(f"Found {len(arbitrage_opps)} arbitrage opportunities!")
        
        for opp in arbitrage_opps:
            with st.expander(f"🎯 {opp['title']} - {opp['profit']:.2%} profit"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Buy on {opp['platform_1']}**")
                    st.markdown(f"Price: {opp['price_1']:.2%}")
                
                with col2:
                    st.markdown(f"**Sell on {opp['platform_2']}**")
                    st.markdown(f"Price: {opp['price_2']:.2%}")
    else:
        st.info("No arbitrage opportunities found at current prices")

st.markdown("---")
st.caption("Data updated every 60 seconds • Built by Digital Insurgent Media")
