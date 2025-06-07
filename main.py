import discord
import os

class MyClient(discord.Client):
    
    # called when the bot is ready
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    # called when a message is received on server
    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        if message.author == self.user:
            return
         
        if message.content.startswith('!hello'):
            await message.channel.send(f'Hello {message.author.name}!')

    async def on_reaction_add(self, reaction, user):
        print(f'Reaction {reaction.emoji} added by {user.name} to message: {reaction.message.content}')
        if user == self.user:
            return
        
        if reaction.emoji == '👍':
            await reaction.message.channel.send(f'Thanks for the thumbs up, {user.name}!')

        
    
# called when a message is sent in a channel the bot can see
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent

# 
token_bot = os.getenv('DISCORD_BOT_TOKEN', "")
client = MyClient(intents=intents)
client.run(token=token_bot)
