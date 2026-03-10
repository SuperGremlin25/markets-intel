# Markets Intel by DIM

Real-time prediction market intelligence platform aggregating data from Polymarket and Kalshi.

## Features

- **Live Market Odds** - Real-time odds from Polymarket and Kalshi
- **Arbitrage Detection** - Find profitable opportunities across platforms
- **Network Analysis** - Visualize market correlations
- **Historical Trends** - Track price movements over time
- **Multi-Sport Coverage** - NBA, NCAA Basketball, UFC, World Events

## Tech Stack

- **Streamlit** - Web framework
- **Plotly** - Interactive visualizations
- **NetworkX** - Network graph analysis
- **Pandas** - Data processing

## Installation

```bash
pip install -r requirements.txt
```

## Running Locally

```bash
streamlit run streamlit_app.py
```

## Deployment

Deploy to Streamlit Cloud:

1. Push to GitHub
2. Connect to Streamlit Cloud
3. Deploy from main branch

## Project Structure

```
prediction-markets-app/
├── streamlit_app.py       # Main application
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── utils/
│   ├── api_client.py      # Polymarket/Kalshi API clients
│   ├── data_processor.py  # Data transformation
│   └── visualizations.py  # Chart generators
└── README.md
```

## API Sources

- **Polymarket**: https://gamma-api.polymarket.com
- **Kalshi**: https://api.elections.kalshi.com/trade-api/v2

## Monetization

- Affiliate links for DraftKings, FanDuel, BetMGM
- Premium features (coming soon)
- API access (coming soon)

## License

MIT License - Digital Insurgent Media
