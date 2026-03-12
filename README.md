# Markets Intel Lite

Real-time prediction market odds and regional intelligence monitoring for Oklahoma.

## Features

### 📊 Live Market Odds
- Real-time odds from Polymarket
- Organized by category (Politics, Sports, Crypto, etc.)
- Direct links to markets

### 🛡️ Intelligence Monitoring
- **Power Grid Status** - Oklahoma & Texas outage tracking
- **Cyber Threats** - CISA security alerts and CVEs
- **Local News** - Oklahoma news aggregation with sentiment analysis

## Tech Stack

- **Streamlit** - Web framework
- **Plotly** - Interactive visualizations
- **VADER** - Sentiment analysis
- **Folium** - Interactive maps
- **Supabase** - Database (optional)

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/SuperGremlin25/markets-intel.git
cd markets-intel
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

4. Run the app:
```bash
streamlit run streamlit_app.py
```

App will be available at http://localhost:8501

## Deployment

### Deploy to Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Deploy from main branch
5. Add secrets in Streamlit Cloud settings (optional)

## Environment Variables

Optional in `.env` or Streamlit Cloud secrets:

```env
# Optional: Supabase (for historical data)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Optional: Groq API (for AI features)
GROQ_API_KEY=your_groq_api_key
```

## Project Structure

```
markets-intel/
├── streamlit_app.py           # Main application
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
├── utils/
│   ├── api_client.py         # Polymarket API
│   ├── power_grid_monitor.py # Power outage tracking
│   ├── cyber_monitor.py      # CISA alerts
│   ├── local_news_monitor.py # News aggregation (OK only)
│   ├── sentiment_analyzer.py # VADER sentiment
│   ├── db_manager.py         # Supabase integration
│   ├── data_processor.py     # Data transformation
│   └── visualizations.py     # Chart generators
└── README.md
```

## Data Sources

- **Polymarket** - Prediction market odds
- **PowerOutage.us** - Power grid status
- **CISA** - Cybersecurity alerts
- **Google News RSS** - Oklahoma local news

## License

MIT License - Digital Insurgent Media

## Links

- Website: [digital-insurgent-media.com](https://digital-insurgent-media.com)
- Live App: [markets.digital-insurgent-media.com](https://markets.digital-insurgent-media.com)
