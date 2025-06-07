# Tradisb - Trading Discord Bot

A Discord bot that monitors Binance cryptocurrency markets and automatically broadcasts trading signals to Discord channels. The bot fetches top gainers from Binance every 5 minutes and shares them with your Discord community.

## Features

- **Automated Trading Signals**: Fetches top 3 gaining cryptocurrencies from Binance every 5 minutes
- **Multi-Channel Broadcasting**: Sends signals to all text channels where the bot has permissions
- **Interactive Commands**: Responds to `!hello` command
- **Reaction Handling**: Responds to 👍 reactions on messages
- **Real-time Market Data**: Uses Binance API for live cryptocurrency price data

## Prerequisites

- Python 3.7+
- Discord Bot Token
- Binance API credentials (optional for basic functionality)

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

### Binance API Keys (Optional)
1. Log in to [Binance](https://www.binance.com/)
2. Go to API Management in your account settings
3. Create a new API key
4. Enable "Enable Reading" permission

## Bot Permissions

The bot requires the following Discord permissions:
- Send Messages
- Read Message History
- Add Reactions
- Use External Emojis

## Usage

1. Clone the repository
2. Install dependencies
3. Set up your `.env` file with the required tokens
4. Run the bot:

```bash
python main.py
```

## Bot Commands

- `!hello` - Bot responds with a greeting
- React with 👍 to any message - Bot will thank you

## How It Works

The bot automatically:
1. Connects to Discord when started
2. Fetches the top 3 gaining cryptocurrencies from Binance every 5 minutes
3. Broadcasts trading signals to all accessible text channels
4. Continues monitoring until stopped

## Example Signal Output

```
📈 Signal: BTCUSDT is up 5.23% in 24h. Price: 45234.56
```

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- The `.env` file is already included in [.gitignore](.gitignore)
- Use read-only Binance API keys for security

## Contributing

Feel free to submit issues and enhancement requests!