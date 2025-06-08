# Tradisb - Trading Discord Bot

A Discord bot that monitors Binance cryptocurrency markets and provides interactive trading features. The bot can fetch real-time price data, create pseudo orders, monitor trading signals, and automatically broadcast order fills to Discord channels.

## Features

- **Real-time Price Queries**: Get current cryptocurrency prices with `!price` command
- **Pseudo Order Management**: Create and track virtual trading orders with `!order` command
- **Trading Dashboard**: View active signals and pending orders with `!signals` command
- **Automated Order Processing**: Bot monitors and simulates order fills every 5 seconds
- **Multi-Channel Broadcasting**: Sends order fill notifications to all accessible text channels
- **Interactive Commands**: Responds to various commands and reactions
- **Signal Generation**: Automatically generates trading signals based on market criteria

## Prerequisites

- Python 3.7+
- Discord Bot Token
- Binance API credentials

## Required Dependencies

```bash
pip install discord.py python-binance
```

## Environment Setup

Create a `.env` file in the project root with the following variables:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here
```

## How to Get API Keys

### Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section
4. Create a bot and copy the token

### Binance API Keys
1. Log in to [Binance](https://www.binance.com/)
2. Go to API Management in your account settings
3. Create a new API key
4. Enable "Enable Reading" permission (read-only is sufficient)

## Bot Permissions

The bot requires the following Discord permissions:
- Send Messages
- Read Message History
- Add Reactions
- Use External Emojis

## Installation & Usage

1. Clone the repository
2. Install dependencies: `pip install discord.py python-binance`
3. Set up your `.env` file with the required tokens
4. Run the bot:

```bash
python main.py
```

## Bot Commands

### 🏠 Basic Commands

- **`!hello`** - Bot responds with a greeting
- **👍 reaction** - React with thumbs up to any message, bot will thank you

### 💰 Price Commands

- **`!price BTC`** - Get current Bitcoin price
- **`!price BTCUSDT`** - Get specific trading pair price
- **`!price ETH`** - Get Ethereum price (automatically adds USDT)

**Example Output:**
```
📈 BTCUSDT
💰 Price: $45,234.56
📊 24h Change: +5.23%
📈 24h Volume: 1,234,567.89
```

### 📊 Order Commands

- **`!order BUY BTCUSDT 0.001`** - Create a pseudo BUY order
- **`!order SELL ETHUSDT 0.1`** - Create a pseudo SELL order

**Example Output:**
```
✅ Pseudo Order Created
🆔 ID: ORDER_1_BTCUSDT_1640995200
📊 BUY 0.001 BTCUSDT
💰 Price: $45,234.5600
⏰ Created: 2023-12-31 12:00:00
```

### 📈 Dashboard Commands

- **`!signals`** - View trading dashboard with active signals and pending orders

**Example Output:**
```
📈 Trading Dashboard

🔔 Active Signals (2):
🟢 BTCUSDT BUY @ $45,234.5600 (+7.50%)
🔴 ETHUSDT SELL @ $3,000.0000 (-6.20%)

⏳ Pending Orders (1):
🟢 BUY 0.001 BTCUSDT @ $45,234.5600
```

## How It Works

### Trading Signal Generation
The bot automatically generates trading signals based on these criteria:
- Price change > 5% in 24 hours
- Trading volume > 1,000
- Confidence score calculated based on price change magnitude

### Pseudo Order System
- Orders are simulated, not real trades
- Orders fill when market price is within 1% of order price
- Orders automatically cancel after 5 minutes if not filled
- All order activities are tracked and reported

### Automated Monitoring
The bot runs a background task that:
1. Checks pending orders every 5 seconds
2. Compares current market prices with order prices
3. Simulates order fills based on price proximity
4. Broadcasts fill notifications to all channels

## Order Fill Logic

Orders are filled when:
- ✅ Market price is within 1% of order price
- ✅ Order status is PENDING
- ✅ Order is less than 5 minutes old

Orders are cancelled when:
- ❌ Order is older than 5 minutes
- ❌ Market price moves too far from order price

## Example Workflow

1. **Check Price**: `!price BTC`
   ```
   📈 BTCUSDT
   💰 Price: $45,000.00
   📊 24h Change: +3.50%
   ```

2. **Create Order**: `!order BUY BTCUSDT 0.001`
   ```
   ✅ Pseudo Order Created
   🆔 ID: ORDER_1_BTCUSDT_1640995200
   📊 BUY 0.001 BTCUSDT
   💰 Price: $45,000.0000
   ```

3. **Monitor Dashboard**: `!signals`
   ```
   📈 Trading Dashboard
   ⏳ Pending Orders (1):
   🟢 BUY 0.001 BTCUSDT @ $45,000.0000
   ```

4. **Automatic Fill Notification** (when price moves within 1%):
   ```
   ✅ Order Filled
   🆔 ORDER_1_BTCUSDT_1640995200
   📊 BUY 0.001 BTCUSDT
   💰 Fill Price: $45,200.0000
   ```

## Configuration

### Signal Criteria (in src/schema.py)
- **Minimum price change**: 5%
- **Minimum volume**: 1,000
- **Order fill tolerance**: 1%
- **Order timeout**: 5 minutes
- **Signal age limit**: 10 minutes

### Bot Settings (in main.py)
- **Monitoring interval**: 5 seconds
- **Binance testnet**: Enabled by default
- **Max signals displayed**: 5
- **Max orders displayed**: 3

## File Structure

```
tradisb/
├── main.py              # Main bot application
├── src/
│   ├── __init__.py
│   └── schema.py        # Trading logic and data models
├── tests/
│   ├── __init__.py
│   └── test_trading_signal.py  # Unit tests
├── .env                 # Environment variables (create this)
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## Testing

Run the test suite to verify functionality:

```bash
pytest
```

## Security Notes

- 🔒 Keep your `.env` file secure and never commit it to version control
- 🔒 The `.env` file is already included in `.gitignore`
- 🔒 Bot uses Binance testnet by default for safety
- 🔒 Use read-only Binance API keys for additional security
- 🔒 All orders are pseudo/simulated - no real trades are executed

## Troubleshooting

### Common Issues

**Bot doesn't respond to commands:**
- Check if bot has "Send Messages" permission
- Verify bot token is correct in `.env`
- Ensure message content intent is enabled

**Price command fails:**
- Verify Binance API credentials
- Check if symbol exists (try adding USDT suffix)
- Ensure internet connection is stable

**Orders not filling:**
- Check if market price is within 1% of order price
- Verify order hasn't expired (5-minute timeout)
- Monitor console output for error messages

### Error Messages

- `❌ Symbol XXXUSDT not found` - Invalid trading pair
- `❌ Order type must be BUY or SELL` - Invalid order type
- `❌ Usage: !order BUY/SELL SYMBOL QUANTITY` - Incorrect command format

## Contributing

Feel free to submit issues and enhancement requests! 

---

**⚠️ Disclaimer**: This bot creates simulated/pseudo orders only. No real trading occurs. Always test thoroughly before using any trading automation in live markets.