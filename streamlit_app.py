import streamlit as st
import pandas as pd
from datetime import datetime
import time
from utils.api_client import fetch_polymarket_markets
from utils.data_processor import normalize_market_data
from utils.db_manager import db
from utils.power_grid_monitor import PowerGridMonitor
from utils.cyber_monitor import CyberThreatMonitor
from utils.local_news_monitor import LocalNewsMonitor
from utils.sentiment_analyzer import score_articles_parallel
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
st.markdown("**Live Prediction Markets + Regional Intelligence**")
st.markdown("Real-time Polymarket odds • Oklahoma intelligence monitoring")

with st.sidebar:
    st.header("⚙️ View Options")
    
    view_mode = st.selectbox(
        "Sort By",
        ["Most Active", "Biggest Movers", "All Markets"]
    )
    
    st.markdown("**Platform:** Polymarket")
    st.caption("Free public version")
    
    st.markdown("---")
    st.markdown("### 🔗 Trade on Polymarket")
    st.markdown("[Sign up for Polymarket](https://polymarket.com)")
    st.caption("Start trading prediction markets")

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

@st.cache_data(ttl=900, show_spinner=False)
def get_cached_news_data():
    news_monitor = LocalNewsMonitor()
    data = news_monitor.get_all_news_parallel(hours=24)
    scored_articles = score_articles_parallel(data['all_articles'])
    scored_articles.sort(key=lambda x: x.get('sentiment_score', 0))
    
    categorized = {
        'power': [],
        'crime': [],
        'cyber': [],
        'emergency': [],
        'weather': []
    }
    
    for article in scored_articles:
        for category in article.get('categories', []):
            categorized.setdefault(category, []).append(article)
    
    data['all_articles'] = scored_articles
    data['by_category'] = categorized
    
    return {
        'data': data,
        'fetched_at': time.time()
    }

tab1, tab2 = st.tabs(["📊 Live Odds", "🛡️ Intelligence"])

with tab1:
    st.header("Live Market Odds")
    
    if markets:
        st.success(f"Found {len(markets)} active markets")
        
        # Group by category
        categories = {}
        for market in markets:
            cat = market.get('category', 'Other')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(market)
        
        # Category filter
        selected_category = st.selectbox(
            "Filter by Category",
            ["All Categories"] + sorted(categories.keys()),
            index=0
        )
        
        # Prepare data for display
        display_markets = []
        if selected_category == "All Categories":
            display_markets = markets
        else:
            display_markets = categories.get(selected_category, [])
        
        # Create DataFrame for display
        table_data = []
        for market in display_markets:
            table_data.append({
                'Category': market.get('category', 'Other'),
                'Market': market['title'],
                'Yes Price': market['yes_price'],
                'No Price': market['no_price'],
                'URL': market['url']
            })
        
        if table_data:
            df = pd.DataFrame(table_data)
            
            # Search box
            search = st.text_input("🔍 Search markets", placeholder="Type to filter...")
            if search:
                df = df[df['Market'].str.contains(search, case=False, na=False)]
            
            st.caption(f"Showing {len(df)} markets")
            
            # Display interactive table
            st.dataframe(
                df,
                column_config={
                    "Category": st.column_config.TextColumn("Category", width="small"),
                    "Market": st.column_config.TextColumn("Market", width="large"),
                    "Yes Price": st.column_config.NumberColumn(
                        "Yes",
                        format="$%.2f",
                        width="small"
                    ),
                    "No Price": st.column_config.NumberColumn(
                        "No",
                        format="$%.2f",
                        width="small"
                    ),
                    "URL": st.column_config.LinkColumn(
                        "Trade",
                        display_text="View →",
                        width="small"
                    )
                },
                hide_index=True,
                use_container_width=True,
                height=600
            )
    else:
        st.info("No markets found for selected filters")

with tab2:
    st.header("🛡️ Oklahoma Intelligence")
    st.markdown("**Real-time monitoring: Power Grid • Cyber Threats • Local News**")
    
    # Power Grid Status
    with st.expander("⚡ Power Grid Status", expanded=True):
        with st.spinner("Checking power grid status..."):
            try:
                power_monitor = PowerGridMonitor()
                grid_summary = power_monitor.get_summary()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    status_color = "🟢" if grid_summary['status'] == 'normal' else "🟡" if grid_summary['status'] == 'warning' else "🔴"
                    st.metric(
                        "Grid Health",
                        f"{grid_summary['grid_health_score']}/10",
                        help="10 = Perfect, 0 = Major Outages"
                    )
                    st.markdown(f"{status_color} **{grid_summary['status'].upper()}**")
                
                with col2:
                    st.metric(
                        "Customers Out",
                        f"{grid_summary['total_customers_out']:,}",
                        help="Total customers without power in OK/TX"
                    )
                
                with col3:
                    st.metric(
                        "Major Outages",
                        len(grid_summary['major_outages']),
                        help="Outages affecting >5,000 customers or >5%"
                    )
                
                if grid_summary['oklahoma_outages']:
                    st.markdown("**Oklahoma Outages:**")
                    for outage in grid_summary['oklahoma_outages']:
                        st.markdown(f"• {outage['utility']}: {outage['customers_out']:,} customers ({outage['percent_out']:.1f}%)")
                
                if grid_summary['texas_outages']:
                    st.markdown("**Texas Outages:**")
                    for outage in grid_summary['texas_outages']:
                        st.markdown(f"• {outage['utility']}: {outage['customers_out']:,} customers ({outage['percent_out']:.1f}%)")
                
                if grid_summary['major_outages']:
                    st.warning("⚠️ Major Outages Detected")
                    for outage in grid_summary['major_outages']:
                        st.markdown(f"**{outage['utility']}** ({outage['state']}): {outage['reason']}")
                
                # Show outages on map
                if st.button("🗺️ View Outage Map", key="power_map"):
                    try:
                        import folium
                        from streamlit_folium import folium_static
                        
                        m = folium.Map(location=[34.5, -98.5], zoom_start=6)
                        
                        all_outages = grid_summary['oklahoma_outages'] + grid_summary['texas_outages']
                        for outage in all_outages:
                            locations = {
                                'OG&E': [35.4676, -97.5164],
                                'PSO': [36.1540, -95.9928],
                                'Oncor': [32.7767, -96.7970],
                                'CenterPoint Energy': [29.7604, -95.3698]
                            }
                            
                            loc = locations.get(outage['utility'], [34.5, -98.5])
                            
                            folium.CircleMarker(
                                location=loc,
                                radius=min(outage['customers_out'] / 100, 20),
                                popup=f"{outage['utility']}<br>{outage['customers_out']:,} customers out<br>{outage['percent_out']:.1f}%",
                                color='red',
                                fill=True,
                                fillColor='red',
                                fillOpacity=0.6
                            ).add_to(m)
                        
                        folium_static(m)
                    except ImportError:
                        st.info("Install streamlit-folium to view maps: pip install streamlit-folium")
                
            except Exception as e:
                st.error(f"Error loading power grid data: {str(e)}")
    
    # Cyber Threat Status
    with st.expander("🔐 Cyber Threat Level", expanded=True):
        with st.spinner("Checking cyber threats..."):
            try:
                cyber_monitor = CyberThreatMonitor()
                cyber_summary = cyber_monitor.get_cyber_intelligence_summary()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    threat_color = "🟢" if cyber_summary['status'] == 'low' else "🟡" if cyber_summary['status'] == 'moderate' else "🟠" if cyber_summary['status'] == 'elevated' else "🔴"
                    st.metric(
                        "Threat Level",
                        f"{cyber_summary['threat_level']}/10",
                        help="0 = Safe, 10 = Critical"
                    )
                    st.markdown(f"{threat_color} **{cyber_summary['status'].upper()}**")
                
                with col2:
                    st.metric(
                        "CISA Alerts (7d)",
                        cyber_summary['total_alerts'],
                        help="Recent cybersecurity alerts from CISA"
                    )
                
                with col3:
                    st.metric(
                        "Service Outages",
                        len(cyber_summary['service_outages']),
                        help="Critical services experiencing issues"
                    )
                
                if cyber_summary['recent_alerts']:
                    st.markdown("**Recent Alerts:**")
                    for alert in cyber_summary['recent_alerts'][:3]:
                        severity_emoji = "🔴" if alert['severity'] == 'critical' else "🟠" if alert['severity'] == 'high' else "🟡"
                        st.markdown(f"{severity_emoji} [{alert['severity'].upper()}] {alert['title']}")
                        st.caption(f"{alert['category']} • {alert['published'][:10]}")
                        if 'link' in alert and alert['link']:
                            st.markdown(f"[🔗 View Alert Details]({alert['link']})")
                
            except Exception as e:
                st.error(f"Error loading cyber threat data: {str(e)}")
    
    # Local News Feed
    with st.expander("📰 Oklahoma News Feed", expanded=False):
        with st.spinner("Loading local news..."):
            try:
                news_result = get_cached_news_data()
                news_data = news_result['data']
                news_age_mins = max(0, int((time.time() - news_result['fetched_at']) / 60))
                
                st.caption(f"News data refreshed {news_age_mins} min ago")
                st.info("📊 **Sentiment Guide:** 🟢 Positive (+0.05 to +1.0) • ⚪ Neutral (-0.05 to +0.05) • 🔴 Negative (-1.0 to -0.05)")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Articles", news_data['total_count'])
                with col2:
                    st.metric("Active Feeds", news_data['successful_count'])
                with col3:
                    negative_articles = len([article for article in news_data['all_articles'] if article.get('sentiment_score', 0) <= -0.05])
                    st.metric("Negative", negative_articles)
                with col4:
                    avg_sentiment = 0
                    if news_data['all_articles']:
                        avg_sentiment = sum([article.get('sentiment_score', 0) for article in news_data['all_articles']]) / len(news_data['all_articles'])
                    st.metric("Avg Sentiment", f"{avg_sentiment:.2f}")
                
                category_order = ['crime', 'weather', 'power', 'cyber', 'emergency']
                for category in category_order:
                    articles = news_data['by_category'].get(category, [])
                    if articles:
                        st.markdown(f"### {category.title()} ({len(articles)} articles)")
                        for article in articles[:5]:
                            st.markdown(f"**[{article['title']}]({article['link']})**")
                            st.caption(f"{article['source']} • {article['city']} • {article['published'][:10]} • {article['sentiment_label']} {article['sentiment_score']:+.2f}")
                            if article.get('summary'):
                                st.markdown(article['summary'])
                        st.markdown("---")
                if not news_data['all_articles']:
                    st.info("No recent local news matched the monitored categories.")
            except Exception as e:
                st.error(f"Error loading local news: {str(e)}")

st.markdown("---")
st.caption("Data updated every 60 seconds • Built by Digital Insurgent Media")
