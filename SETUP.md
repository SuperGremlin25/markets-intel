# Markets Intel - Setup Guide

Complete setup instructions for the Markets Intel platform.

## Prerequisites

- Python 3.9+
- Git
- Discord account
- Stripe account (for payments)
- Supabase account (for database)
- OpenAI API key (for AI predictions)

## Step 1: Clone and Install

```bash
cd C:\Projects\DIM\prediction-markets-app
pip install -r requirements.txt
```

## Step 2: Set Up Supabase Database

1. **Create Supabase Account:**
   - Go to https://supabase.com
   - Create new project
   - Note your project URL and anon key

2. **Create Tables:**

Run these SQL commands in Supabase SQL Editor:

```sql
-- Market snapshots table
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

-- Subscriptions table
CREATE TABLE subscriptions (
    id BIGSERIAL PRIMARY KEY,
    discord_id TEXT UNIQUE NOT NULL,
    email TEXT,
    plan TEXT NOT NULL, -- 'free', 'premium', 'pro'
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_discord_id ON subscriptions(discord_id);
CREATE INDEX idx_subscriptions_stripe_customer ON subscriptions(stripe_customer_id);
```

## Step 3: Set Up Discord Bot

1. **Create Discord Application:**
   - Go to https://discord.com/developers/applications
   - Click "New Application"
   - Name: "Markets Intel Bot"

2. **Create Bot:**
   - Go to "Bot" tab
   - Click "Add Bot"
   - Copy bot token (save for .env)
   - Enable "Message Content Intent"
   - Enable "Server Members Intent"

3. **Get Bot Invite URL:**
   - Go to "OAuth2" → "URL Generator"
   - Scopes: `bot`, `applications.commands`
   - Permissions: 
     - Send Messages
     - Embed Links
     - Manage Roles
     - Read Message History
   - Copy generated URL

4. **Create Discord Server:**
   - Open Discord
   - Click "+" → "Create My Own" → "For a club or community"
   - Name: "Markets Intel"
   - Paste bot invite URL in browser
   - Select your server → Authorize

5. **Get Server and Role IDs:**
   - Enable Developer Mode: Settings → Advanced → Developer Mode
   - Right-click server name → Copy ID (this is GUILD_ID)
   - Create roles: "Premium" and "Pro"
   - Right-click each role → Copy ID (save for .env)

## Step 4: Set Up OpenAI

1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Copy key (save for .env)

## Step 5: Set Up Stripe

1. **Create Stripe Account:**
   - Go to https://dashboard.stripe.com/register
   - Complete setup

2. **Get API Keys:**
   - Dashboard → Developers → API keys
   - Copy "Secret key" (save for .env)

3. **Create Products:**
   - Dashboard → Products → Add product
   - Create "Premium" ($29/month recurring)
   - Create "Pro" ($99/month recurring)
   - Copy each Price ID (save for .env)

4. **Set Up Webhook:**
   - Dashboard → Developers → Webhooks
   - Add endpoint: `https://your-app-url/webhook/stripe`
   - Select events: `checkout.session.completed`, `customer.subscription.deleted`
   - Copy webhook secret (save for .env)

## Step 6: Configure Environment Variables

Create `.env` file in project root:

```bash
# Copy from .env.example
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_anon_key_here

# OpenAI
OPENAI_API_KEY=sk-xxxxx

# Discord
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_GUILD_ID=your_server_id
DISCORD_PREMIUM_ROLE_ID=your_premium_role_id
DISCORD_PRO_ROLE_ID=your_pro_role_id

# Stripe
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
STRIPE_PREMIUM_PRICE_ID=price_xxxxx
STRIPE_PRO_PRICE_ID=price_xxxxx
```

## Step 7: Run Locally

```bash
# Start Streamlit app
streamlit run streamlit_app.py

# In separate terminal, start Discord bot
python discord_bot.py
```

App will be available at http://localhost:8501

## Step 8: Deploy to Streamlit Cloud

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Initial Markets Intel setup"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your repo
   - Main file: `streamlit_app.py`
   - Click "Advanced settings"
   - Add all environment variables from `.env`
   - Click "Deploy"

3. **Deploy Discord Bot:**
   - Use Railway.app or Replit
   - Connect GitHub repo
   - Set start command: `python discord_bot.py`
   - Add environment variables
   - Deploy

## Step 9: Integrate with Your Website

Add to `digital-insurgent-media.com`:

```tsx
// src/components/MarketsIntel.tsx
export function MarketsIntel() {
  return (
    <div className="min-h-screen bg-[#06060a] p-8">
      <h1 className="text-4xl font-bold mb-4">Markets Intel Terminal</h1>
      <iframe
        src="https://your-app.streamlit.app?embedded=true"
        className="w-full h-[800px] border-0"
      />
    </div>
  );
}
```

## Troubleshooting

**Supabase connection fails:**
- Check URL and key are correct
- Verify tables are created
- Check network/firewall

**Discord bot offline:**
- Verify bot token is correct
- Check intents are enabled
- Ensure bot is invited to server

**Stripe webhooks not working:**
- Use Stripe CLI for local testing: `stripe listen --forward-to localhost:8501/webhook/stripe`
- Verify webhook secret matches
- Check endpoint URL is correct

## Next Steps

1. Invite first users to Discord
2. Test payment flow
3. Monitor for errors
4. Collect feedback
5. Iterate and improve

## Support

For issues, contact: your-email@example.com
Discord: https://discord.gg/your-invite
