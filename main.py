import discord
import os
import asyncio
from binance.client import Client as BinanceClient
# from binance.enums import *

# Setup Binance client
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
binance_client = BinanceClient(
    api_key=BINANCE_API_KEY, 
    api_secret=BINANCE_API_SECRET,
    testnet=True
)

# Discord bot client
class MyClient(discord.Client):
    
    # called when the bot is ready
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

        # Schedule the fetch task
        self.bg_task = self.loop.create_task(self.fetch_trade_signals())

    # called when a message is received on server
    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        if message.author == self.user:
            return
         
        if message.content.startswith('!hello'):
            await message.channel.send(f'Hello {message.author.name}!')
        
        # New feature: Get crypto price
        if message.content.startswith('!price'):
            await self.handle_price_command(message)

    # Handle price command
    async def handle_price_command(self, message):
        try:
            # Extract symbol from command (!price BTC or !price BTCUSDT)
            parts = message.content.split()
            if len(parts) < 2:
                await message.channel.send("❌ Please specify a symbol. Example: `!price BTC` or `!price BTCUSDT`")
                return
            
            symbol = parts[1].upper()
            
            # If symbol doesn't end with USDT, add it
            if not symbol.endswith('USDT'):
                symbol += 'USDT'
            
            # Get ticker data
            ticker = binance_client.get_ticker(symbol=symbol)
            
            # Format the response
            price = float(ticker['lastPrice'])
            change_percent = float(ticker['priceChangePercent'])
            volume = float(ticker['volume'])
            
            # Choose emoji based on price change
            emoji = "📈" if change_percent >= 0 else "📉"
            change_sign = "+" if change_percent >= 0 else ""
            
            response = f"{emoji} **{symbol}**\n"
            response += f"💰 Price: ${price:,.4f}\n"
            response += f"📊 24h Change: {change_sign}{change_percent:.2f}%\n"
            response += f"📈 24h Volume: {volume:,.2f}"
            
            await message.channel.send(response)
            
        except Exception as e:
            error_msg = str(e)
            if "Invalid symbol" in error_msg or "symbol does not exist" in error_msg.lower():
                await message.channel.send(f"❌ Symbol `{symbol}` not found. Please check the symbol name.")
            else:
                await message.channel.send(f"❌ Error fetching price data: {error_msg}")

    # called when a reaction is added to a message
    async def on_reaction_add(self, reaction, user):
        print(f'Reaction {reaction.emoji} added by {user.name} to message: {reaction.message.content}')
        if user == self.user:
            return
        
        if reaction.emoji == '👍':
            await reaction.message.channel.send(f'Thanks for the thumbs up, {user.name}!')

    # called when trade signals are fetched 
    async def fetch_trade_signals(self):
        await self.wait_until_ready()
        channel_ids = [channel.id for guild in self.guilds for channel in guild.text_channels if channel.permissions_for(guild.me).send_messages]
        
        while not self.is_closed():
            print("Fetching trade signals...")
            # Example: Fetch top gainers
            tickers = binance_client.get_ticker_24hr()
            top = sorted(tickers, key=lambda x: float(x['priceChangePercent']), reverse=True)[:3]

            for symbol in top:
                msg = f"📈 Signal: {symbol['symbol']} is up {symbol['priceChangePercent']}% in 24h. Price: {symbol['lastPrice']}"
                await self.broadcast_message(channel_ids, msg)

            await asyncio.sleep(300)  # Wait 5 minutes

    # Helper function to broadcast messages to all channels
    async def broadcast_message(self, channel_ids, content):
        for channel_id in channel_ids:
            channel = self.get_channel(channel_id)
            if channel:
                try:
                    await channel.send(content)
                except discord.Forbidden:
                    continue

# Setup bot
intents = discord.Intents.default()
intents.message_content = True

token_bot = os.getenv('DISCORD_BOT_TOKEN', '')
client = MyClient(intents=intents)
client.run(token=token_bot)