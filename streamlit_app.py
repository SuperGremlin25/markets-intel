import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from utils.api_client import fetch_polymarket_markets, fetch_kalshi_markets
from utils.data_processor import normalize_market_data, calculate_arbitrage
from utils.visualizations import create_odds_chart, create_network_map
import config

st.set_page_config(
    page_title="Markets Intel by DIM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Markets Intel by DIM")
st.markdown("**Real-time prediction market intelligence from Polymarket and Kalshi**")

with st.sidebar:
    st.header("⚙️ Filters")
    
    category = st.selectbox(
        "Category",
        ["All", "NBA", "NCAA Basketball", "UFC", "World Events"]
    )
    
    platform = st.selectbox(
        "Platform",
        ["Both", "Polymarket", "Kalshi"]
    )
    
    st.markdown("---")
    st.markdown("### 💰 Start Betting")
    st.markdown("[Get $1000 Bonus - DraftKings](https://draftkings.com)")
    st.markdown("[Get $500 Bonus - FanDuel](https://fanduel.com)")
    st.markdown("*Affiliate links - we may earn commission*")

def load_market_data(category_filter, platform_filter):
    polymarket_data = []
    kalshi_data = []
    
    if platform_filter in ["Both", "Polymarket"]:
        polymarket_data = fetch_polymarket_markets(category_filter)
    
    if platform_filter in ["Both", "Kalshi"]:
        kalshi_data = fetch_kalshi_markets(category_filter)
    
    combined_data = polymarket_data + kalshi_data
    return combined_data

with st.spinner("Loading market data..."):
    markets = load_market_data(category, platform)

tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Odds", "📈 Historical Trends", "🕸️ Network Analysis", "💎 Arbitrage"])

with tab1:
    st.header("Live Market Odds")
    
    if markets:
        st.success(f"Found {len(markets)} active markets")
        
        for idx, market in enumerate(markets[:20]):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{market['title']}**")
                st.caption(f"{market['platform']} • {market['category']}")
            
            with col2:
                st.metric("Yes", f"{market['yes_price']:.1%}")
            
            with col3:
                st.metric("No", f"{market['no_price']:.1%}")
            
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
