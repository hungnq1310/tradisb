import discord
import os
import asyncio
from binance.client import Client as BinanceClient
from src.schema import TradingSignalValidator, OrderType
# from binance.enums import *

# Setup Binance client
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
binance_client = BinanceClient(
    api_key=BINANCE_API_KEY, 
    api_secret=BINANCE_API_SECRET,
    testnet=True
)

# Initialize trading validator
trading_validator = TradingSignalValidator(binance_client)

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
            
        # New feature: Create pseudo order
        if message.content.startswith('!order'):
            await self.handle_order_command(message)
            
        # New feature: Check signals
        if message.content.startswith('!signals'):
            await self.handle_signals_command(message)

    # Handle order command
    async def handle_order_command(self, message):
        try:
            # Format: !order BUY BTCUSDT 0.001
            parts = message.content.split()
            if len(parts) < 4:
                await message.channel.send("❌ Usage: `!order BUY/SELL SYMBOL QUANTITY`\nExample: `!order BUY BTCUSDT 0.001`")
                return
                
            order_type = parts[1].upper()
            symbol = parts[2].upper()
            quantity = float(parts[3])
            
            if order_type not in ['BUY', 'SELL']:
                await message.channel.send("❌ Order type must be BUY or SELL")
                return
                
            # Get current price
            ticker = binance_client.get_ticker(symbol=symbol)
            current_price = float(ticker['lastPrice'])
            
            # Create a mock signal for the order
            from src.schema import TradingSignal
            from datetime import datetime
            
            signal = TradingSignal(
                symbol=symbol,
                signal_type=order_type,
                price=current_price,
                change_percent=float(ticker['priceChangePercent']),
                volume=float(ticker['volume']),
                timestamp=datetime.now(),
                confidence=0.8
            )
            
            order = trading_validator.create_pseudo_order(signal, quantity)
            
            response = f"✅ **Pseudo Order Created**\n"
            response += f"🆔 ID: {order.id}\n"
            response += f"📊 {order.order_type.value} {order.quantity} {order.symbol}\n"
            response += f"💰 Price: ${order.price:,.4f}\n"
            response += f"⏰ Created: {order.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            
            await message.channel.send(response)
            
        except Exception as e:
            await message.channel.send(f"❌ Error creating order: {str(e)}")

    # Handle signals command
    async def handle_signals_command(self, message):
        active_signals = trading_validator.get_active_signals()
        pending_orders = trading_validator.get_pending_orders()
        
        if not active_signals and not pending_orders:
            await message.channel.send("📊 No active signals or pending orders found.")
            return
            
        response = "📈 **Trading Dashboard**\n\n"
        
        if active_signals:
            response += f"🔔 **Active Signals ({len(active_signals)}):**\n"
            for signal in active_signals[-5:]:  # Show last 5
                emoji = "🟢" if signal.signal_type == "BUY" else "🔴"
                response += f"{emoji} {signal.symbol} {signal.signal_type} @ ${signal.price:,.4f} ({signal.change_percent:+.2f}%)\n"
            response += "\n"
            
        if pending_orders:
            response += f"⏳ **Pending Orders ({len(pending_orders)}):**\n"
            for order in pending_orders[-3:]:  # Show last 3
                emoji = "🟢" if order.order_type == OrderType.BUY else "🔴"
                response += f"{emoji} {order.order_type.value} {order.quantity} {order.symbol} @ ${order.price:,.4f}\n"
                
        await message.channel.send(response)

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
            tickers = binance_client.get_ticker()
            
            # TODO: Not Generate signals for qualifying tickers HERE
            for ticker in tickers:
                signal = trading_validator.generate_trading_signal(ticker)
                if signal:
                    msg = f"🚨 **Trading Signal Detected**\n"
                    msg += f"📊 {signal.symbol} {signal.signal_type}\n"
                    msg += f"💰 Price: ${signal.price:,.4f}\n"
                    msg += f"📈 Change: {signal.change_percent:+.2f}%\n"
                    msg += f"🎯 Confidence: {signal.confidence:.1%}"
                    await self.broadcast_message(channel_ids, msg)
            
            # Process pending orders
            pending_orders = trading_validator.get_pending_orders()
            for order in pending_orders:
                try:
                    current_ticker = binance_client.get_ticker(symbol=order.symbol)
                    current_price = float(current_ticker['lastPrice'])
                    
                    if trading_validator.simulate_order_fill(order, current_price):
                        fill_msg = f"✅ **Order Filled**\n"
                        fill_msg += f"🆔 {order.id}\n"
                        fill_msg += f"📊 {order.order_type.value} {order.quantity} {order.symbol}\n"
                        fill_msg += f"💰 Fill Price: ${order.fill_price:,.4f}"
                        await self.broadcast_message(channel_ids, fill_msg)
                except Exception as e:
                    print(f"Error processing order {order.id}: {e}")

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