# Markets Intel - Quick Start Guide

Get up and running in 10 minutes!

## What We've Built So Far

✅ **Streamlit App** - Dark terminal theme, sorting by Most Active/Biggest Movers
✅ **Discord Bot** - Automated alerts for trending markets, big movers, Heavy Hitter trades, arbitrage
✅ **Database Manager** - Supabase integration for historical data
✅ **API Integration** - Polymarket and Kalshi real-time data

## Next Steps to Get Running

### 1. Install Dependencies (2 minutes)

```bash
cd C:\Projects\DIM\prediction-markets-app
pip install -r requirements.txt
```

### 2. Set Up Environment Variables (3 minutes)

Create `.env` file:

```bash
# Copy example
copy .env.example .env
```

**Minimum required to test locally:**
```env
# Leave these empty for now - app will work without them
SUPABASE_URL=
SUPABASE_KEY=

# Leave empty - AI features will be disabled
OPENAI_API_KEY=

# Leave empty - Discord bot won't run but app will work
DISCORD_BOT_TOKEN=
```

### 3. Test the App (1 minute)

```bash
streamlit run streamlit_app.py
```

App opens at http://localhost:8501

**What you'll see:**
- Markets loading from Polymarket and Kalshi
- Sort by "Most Active" or "Biggest Movers"
- Working "View Market" links
- Arbitrage detection (if markets match)

### 4. Optional: Set Up Supabase (5 minutes)

Only needed for historical data and 24hr price changes.

1. Go to https://supabase.com
2. Create free account
3. Create new project
4. Go to SQL Editor
5. Run this SQL:

```sql
CREATE TABLE market_snapshots (
    id BIGSERIAL PRIMARY KEY,
    market_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    title TEXT,
    category TEXT,
    yes_price DECIMAL(10,4),
    no_price DECIMAL(10,4),
    volume DECIMAL(15,2),
    liquidity DECIMAL(15,2),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_market_snapshots_market_id ON market_snapshots(market_id);
CREATE INDEX idx_market_snapshots_timestamp ON market_snapshots(timestamp);
```

6. Get your URL and anon key from Settings → API
7. Add to `.env`:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_anon_key_here
```

8. Restart app - it will now store historical data!

### 5. Optional: Set Up Discord Bot (10 minutes)

Follow the detailed guide in `SETUP.md` sections 3-5.

**Quick version:**
1. Create Discord application at https://discord.com/developers/applications
2. Create bot, copy token
3. Create Discord server
4. Invite bot to server
5. Add token to `.env`
6. Run bot: `python discord_bot.py`

## What's Working Now

### Streamlit App Features
- ✅ Real-time market data from Polymarket and Kalshi
- ✅ Sort by Most Active (volume) or Biggest Movers (price change)
- ✅ Platform filter (Both, Polymarket, Kalshi)
- ✅ Arbitrage detection
- ✅ Working market links
- ✅ Dark terminal theme
- ⏳ Historical trends (needs 24hrs of data)
- ⏳ AI predictions (needs OpenAI key)
- ⏳ Sentiment analysis (coming Day 2)

### Discord Bot Features
- ✅ Commands: `!markets`, `!price`, `!arbitrage`, `!help`
- ✅ Automated trending markets (hourly)
- ✅ Automated big movers (6-hourly)
- ✅ Automated arbitrage alerts (15min)
- ✅ Heavy Hitter alerts (Premium feature)
- ⏳ Role-based access control (needs Stripe)

## Troubleshooting

**"Module not found" errors:**
```bash
pip install -r requirements.txt
```

**Markets not loading:**
- Check internet connection
- Polymarket/Kalshi APIs may be down (rare)
- Try refreshing the page

**Database errors:**
- App works without database
- Historical features just won't show data
- Set up Supabase to enable them

**Discord bot won't start:**
- Check `DISCORD_BOT_TOKEN` in `.env`
- Make sure bot has correct intents enabled
- See full setup in `SETUP.md`

## What's Next

**Day 2 (Tomorrow):**
- Add sentiment analysis (Twitter, Telegram, News)
- Display sentiment scores on markets
- Sentiment-based alerts in Discord

**Day 3:**
- OpenAI GPT-4 integration
- AI market predictions
- Confidence scoring

**Day 4:**
- Historical trends charts
- Pattern recognition
- Price movement visualization

**Day 5-7:**
- Stripe payments
- Discord role automation
- Deploy to production
- Launch!

## Current Status

**App is functional and ready to use locally!** 

You can:
- Browse markets
- Find arbitrage opportunities
- Sort by activity or price movement
- Click through to trade

The core intelligence features (AI predictions, sentiment, historical trends) will be added over the next few days.

## Need Help?

- Full setup guide: `SETUP.md`
- Implementation plan: `.windsurf/plans/markets-intel-final-plan-7561df.md`
- Discord setup: `SETUP.md` sections 3-5
- Database setup: `SETUP.md` section 2

## Quick Commands

```bash
# Run app
streamlit run streamlit_app.py

# Run Discord bot
python discord_bot.py

# Install dependencies
pip install -r requirements.txt

# Check what's changed
git status

# Commit changes
git add .
git commit -m "Your message"
git push origin main
```

**You're ready to go! 🚀**
