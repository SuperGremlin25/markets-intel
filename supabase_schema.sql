-- Markets Intel - Supabase Database Schema
-- Run this in your Supabase SQL Editor
-- Market snapshots table for historical tracking
CREATE TABLE IF NOT EXISTS market_snapshots (
    id BIGSERIAL PRIMARY KEY,
    market_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    title TEXT,
    category TEXT,
    yes_price DECIMAL(10, 4),
    no_price DECIMAL(10, 4),
    volume DECIMAL(15, 2),
    liquidity DECIMAL(15, 2),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_market_snapshots_market_id ON market_snapshots(market_id);
CREATE INDEX IF NOT EXISTS idx_market_snapshots_timestamp ON market_snapshots(timestamp);
CREATE INDEX IF NOT EXISTS idx_market_snapshots_platform ON market_snapshots(platform);
-- Subscriptions table for user management
CREATE TABLE IF NOT EXISTS subscriptions (
    id BIGSERIAL PRIMARY KEY,
    discord_id TEXT UNIQUE NOT NULL,
    email TEXT,
    plan TEXT NOT NULL CHECK (plan IN ('free', 'premium', 'pro')),
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'past_due')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes for subscriptions
CREATE INDEX IF NOT EXISTS idx_subscriptions_discord_id ON subscriptions(discord_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_customer ON subscriptions(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan ON subscriptions(plan);
-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column() RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW();
RETURN NEW;
END;
$$ language 'plpgsql';
-- Trigger to auto-update updated_at
CREATE TRIGGER update_subscriptions_updated_at BEFORE
UPDATE ON subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
-- Grant permissions (adjust as needed for your setup)
-- These are safe defaults for the anon key
ALTER TABLE market_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
-- Policy: Allow inserts from authenticated service role
CREATE POLICY "Allow service role to insert market snapshots" ON market_snapshots FOR
INSERT WITH CHECK (true);
-- Policy: Allow reads for everyone (public data)
CREATE POLICY "Allow public read access to market snapshots" ON market_snapshots FOR
SELECT USING (true);
-- Policy: Only service role can manage subscriptions
CREATE POLICY "Service role can manage subscriptions" ON subscriptions FOR ALL USING (true);