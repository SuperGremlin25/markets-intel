"""
Markets Intel Discord Bot
Automated alerts for whale trades, arbitrage, AI predictions, and market trends
"""

import os
import asyncio
from datetime import datetime
from typing import List, Dict
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from utils.api_client import fetch_polymarket_markets, fetch_kalshi_markets
from utils.data_processor import calculate_arbitrage
from utils.db_manager import db

load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Channel IDs (will be set after bot starts)
TRENDING_CHANNEL_ID = None
BIG_MOVERS_CHANNEL_ID = None
HEAVY_HITTER_ALERTS_CHANNEL_ID = None
ARBITRAGE_CHANNEL_ID = None

# Role IDs
PREMIUM_ROLE_ID = int(os.getenv('DISCORD_PREMIUM_ROLE_ID', 0))
PRO_ROLE_ID = int(os.getenv('DISCORD_PRO_ROLE_ID', 0))

def has_premium_role(member: discord.Member) -> bool:
    """Check if user has Premium or Pro role"""
    if not member:
        return False
    role_ids = [role.id for role in member.roles]
    return PREMIUM_ROLE_ID in role_ids or PRO_ROLE_ID in role_ids

def has_pro_role(member: discord.Member) -> bool:
    """Check if user has Pro role"""
    if not member:
        return False
    role_ids = [role.id for role in member.roles]
    return PRO_ROLE_ID in role_ids

@bot.event
async def on_ready():
    """Bot startup event"""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    
    # Start background tasks
    post_trending_markets.start()
    post_big_movers.start()
    check_arbitrage_opportunities.start()
    
    print('Background tasks started')

@tasks.loop(hours=1)
async def post_trending_markets():
    """Post top 10 trending markets every hour"""
    try:
        if not TRENDING_CHANNEL_ID:
            return
        
        channel = bot.get_channel(TRENDING_CHANNEL_ID)
        if not channel:
            return
        
        # Fetch markets
        polymarket_data = fetch_polymarket_markets('All')
        kalshi_data = fetch_kalshi_markets('All')
        all_markets = polymarket_data + kalshi_data
        
        # Sort by volume
        all_markets.sort(key=lambda x: x.get('volume', 0), reverse=True)
        top_markets = all_markets[:10]
        
        # Create embed
        embed = discord.Embed(
            title="🔥 Top 10 Trending Markets",
            description=f"Updated: {datetime.now().strftime('%I:%M %p')}",
            color=0x00ff88,
            timestamp=datetime.now()
        )
        
        for i, market in enumerate(top_markets, 1):
            yes_price = market['yes_price']
            volume = market.get('volume', 0)
            platform = market['platform']
            
            embed.add_field(
                name=f"{i}. {market['title'][:100]}",
                value=f"**{platform}** | Yes: {yes_price:.1%} | Volume: ${volume:,.0f}\n[View Market]({market['url']})",
                inline=False
            )
        
        embed.set_footer(text="Markets Intel by DIM")
        await channel.send(embed=embed)
        
    except Exception as e:
        print(f"Error posting trending markets: {e}")

@tasks.loop(hours=6)
async def post_big_movers():
    """Post biggest price movers every 6 hours"""
    try:
        if not BIG_MOVERS_CHANNEL_ID:
            return
        
        channel = bot.get_channel(BIG_MOVERS_CHANNEL_ID)
        if not channel:
            return
        
        # Fetch markets
        polymarket_data = fetch_polymarket_markets('All')
        kalshi_data = fetch_kalshi_markets('All')
        all_markets = polymarket_data + kalshi_data
        
        # Calculate 24hr changes
        movers = []
        for market in all_markets:
            change = db.get_24hr_price_change(market['id'])
            if change is not None and abs(change) > 0.05:  # >5% change
                market['change'] = change
                movers.append(market)
        
        # Sort by absolute change
        movers.sort(key=lambda x: abs(x['change']), reverse=True)
        top_movers = movers[:10]
        
        if not top_movers:
            return
        
        # Create embed
        embed = discord.Embed(
            title="📈 Biggest Movers (24hr)",
            description=f"Updated: {datetime.now().strftime('%I:%M %p')}",
            color=0xff0040,
            timestamp=datetime.now()
        )
        
        for i, market in enumerate(top_movers, 1):
            change = market['change']
            arrow = "🔺" if change > 0 else "🔻"
            
            embed.add_field(
                name=f"{i}. {market['title'][:100]}",
                value=f"{arrow} **{change:+.1%}** | {market['platform']} | Yes: {market['yes_price']:.1%}\n[View Market]({market['url']})",
                inline=False
            )
        
        embed.set_footer(text="Markets Intel by DIM")
        await channel.send(embed=embed)
        
    except Exception as e:
        print(f"Error posting big movers: {e}")

@tasks.loop(minutes=15)
async def check_arbitrage_opportunities():
    """Check for arbitrage opportunities every 15 minutes (Premium feature)"""
    try:
        if not ARBITRAGE_CHANNEL_ID:
            return
        
        channel = bot.get_channel(ARBITRAGE_CHANNEL_ID)
        if not channel:
            return
        
        # Fetch markets
        polymarket_data = fetch_polymarket_markets('All')
        kalshi_data = fetch_kalshi_markets('All')
        all_markets = polymarket_data + kalshi_data
        
        # Find arbitrage opportunities
        opportunities = calculate_arbitrage(all_markets, min_profit=0.02)
        
        if not opportunities:
            return
        
        # Post top 3 opportunities
        for opp in opportunities[:3]:
            embed = discord.Embed(
                title="💎 Arbitrage Opportunity Detected",
                description=f"**{opp['title']}**",
                color=0x00d9ff,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name=f"Buy on {opp['platform_1']}",
                value=f"Price: {opp['price_1']:.1%}",
                inline=True
            )
            
            embed.add_field(
                name=f"Sell on {opp['platform_2']}",
                value=f"Price: {opp['price_2']:.1%}",
                inline=True
            )
            
            embed.add_field(
                name="Expected Profit",
                value=f"**{opp['profit']:.1%}**",
                inline=True
            )
            
            embed.set_footer(text="Markets Intel by DIM • Premium Feature")
            await channel.send(embed=embed)
        
    except Exception as e:
        print(f"Error checking arbitrage: {e}")

@bot.command(name='markets')
async def show_markets(ctx):
    """Show trending markets"""
    try:
        # Fetch markets
        polymarket_data = fetch_polymarket_markets('All')
        kalshi_data = fetch_kalshi_markets('All')
        all_markets = polymarket_data + kalshi_data
        
        # Sort by volume
        all_markets.sort(key=lambda x: x.get('volume', 0), reverse=True)
        top_markets = all_markets[:5]
        
        embed = discord.Embed(
            title="📊 Top 5 Markets",
            color=0x00ff88
        )
        
        for i, market in enumerate(top_markets, 1):
            embed.add_field(
                name=f"{i}. {market['title'][:100]}",
                value=f"{market['platform']} | Yes: {market['yes_price']:.1%}",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"Error fetching markets: {e}")

@bot.command(name='price')
async def check_price(ctx, *, market_name: str):
    """Check price for a specific market"""
    try:
        # Fetch markets
        polymarket_data = fetch_polymarket_markets('All')
        kalshi_data = fetch_kalshi_markets('All')
        all_markets = polymarket_data + kalshi_data
        
        # Search for market
        market_name_lower = market_name.lower()
        found_markets = [m for m in all_markets if market_name_lower in m['title'].lower()]
        
        if not found_markets:
            await ctx.send(f"No markets found matching '{market_name}'")
            return
        
        market = found_markets[0]
        
        embed = discord.Embed(
            title=market['title'],
            url=market['url'],
            color=0x00ff88
        )
        
        embed.add_field(name="Platform", value=market['platform'], inline=True)
        embed.add_field(name="Yes Price", value=f"{market['yes_price']:.1%}", inline=True)
        embed.add_field(name="No Price", value=f"{market['no_price']:.1%}", inline=True)
        
        if market.get('volume'):
            embed.add_field(name="Volume", value=f"${market['volume']:,.0f}", inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"Error checking price: {e}")

@bot.command(name='arbitrage')
async def show_arbitrage(ctx):
    """Show arbitrage opportunities (Premium only)"""
    if not has_premium_role(ctx.author):
        await ctx.send("⚠️ This is a Premium feature. Upgrade at https://digital-insurgent-media.com/markets")
        return
    
    try:
        # Fetch markets
        polymarket_data = fetch_polymarket_markets('All')
        kalshi_data = fetch_kalshi_markets('All')
        all_markets = polymarket_data + kalshi_data
        
        # Find arbitrage
        opportunities = calculate_arbitrage(all_markets, min_profit=0.02)
        
        if not opportunities:
            await ctx.send("No arbitrage opportunities found at the moment.")
            return
        
        embed = discord.Embed(
            title="💎 Arbitrage Opportunities",
            color=0x00d9ff
        )
        
        for i, opp in enumerate(opportunities[:5], 1):
            embed.add_field(
                name=f"{i}. {opp['title'][:80]}",
                value=f"Buy {opp['platform_1']} @ {opp['price_1']:.1%} → Sell {opp['platform_2']} @ {opp['price_2']:.1%}\n**Profit: {opp['profit']:.1%}**",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"Error fetching arbitrage: {e}")

@bot.command(name='help')
async def show_help(ctx):
    """Show available commands"""
    embed = discord.Embed(
        title="🤖 Markets Intel Bot Commands",
        description="AI-powered prediction market intelligence",
        color=0x00ff88
    )
    
    embed.add_field(
        name="Free Commands",
        value="`!markets` - Show top 5 trending markets\n`!price [market]` - Check price for a market\n`!help` - Show this message",
        inline=False
    )
    
    embed.add_field(
        name="Premium Commands",
        value="`!arbitrage` - Show arbitrage opportunities\n`!whales` - Show recent whale trades\n`!sentiment [market]` - Check social sentiment",
        inline=False
    )
    
    embed.add_field(
        name="Pro Commands",
        value="`!portfolio` - Analyze your portfolio\n`!follow [wallet]` - Copy-trade a wallet\n`!alert [market] [condition]` - Set custom alert",
        inline=False
    )
    
    embed.set_footer(text="Upgrade at https://digital-insurgent-media.com/markets")
    
    await ctx.send(embed=embed)

async def assign_role(guild_id: int, user_id: int, role_id: int):
    """Assign a role to a user (called from Stripe webhook)"""
    try:
        guild = bot.get_guild(guild_id)
        if not guild:
            print(f"Guild {guild_id} not found")
            return False
        
        member = guild.get_member(user_id)
        if not member:
            print(f"Member {user_id} not found in guild {guild_id}")
            return False
        
        role = guild.get_role(role_id)
        if not role:
            print(f"Role {role_id} not found in guild {guild_id}")
            return False
        
        await member.add_roles(role)
        print(f"Assigned role {role.name} to {member.name}")
        return True
        
    except Exception as e:
        print(f"Error assigning role: {e}")
        return False

async def remove_role(guild_id: int, user_id: int, role_id: int):
    """Remove a role from a user (called when subscription cancelled)"""
    try:
        guild = bot.get_guild(guild_id)
        if not guild:
            return False
        
        member = guild.get_member(user_id)
        if not member:
            return False
        
        role = guild.get_role(role_id)
        if not role:
            return False
        
        await member.remove_roles(role)
        print(f"Removed role {role.name} from {member.name}")
        return True
        
    except Exception as e:
        print(f"Error removing role: {e}")
        return False

if __name__ == '__main__':
    # Get bot token
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables")
        print("Please set up your .env file with Discord credentials")
        exit(1)
    
    # Set channel IDs (you'll need to update these after creating channels)
    # For now, these will be None and tasks won't post
    # Update these in .env after creating Discord channels
    
    print("Starting Markets Intel Discord Bot...")
    print("Make sure to:")
    print("1. Create Discord server")
    print("2. Invite bot to server")
    print("3. Create channels: #trending-markets, #big-movers, #whale-alerts, #arbitrage-opportunities")
    print("4. Update channel IDs in .env")
    print()
    
    bot.run(token)
