import discord
import os
import asyncio
from binance.client import Client as BinanceClient
# from binance.enums import *

# Setup Binance client
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
binance_client = BinanceClient(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)

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
