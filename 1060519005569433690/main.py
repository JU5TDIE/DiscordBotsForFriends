import os
import json
import discord
import asyncpraw
from discord.ext import commands

class Bot(commands.Bot):
    def __init__(self, config):
        super().__init__('', intents=discord.Intents.default())
        self.config = config
        self.initial_extensions = [f'cogs.{filename}'.replace('.py', '') for filename in os.listdir('./cogs') if filename != '__pycache__']

    async def setup_hook(self):
        self.reddit = asyncpraw.Reddit(
        client_id=self.config['reddit']['client_id'],
        client_secret=self.config['reddit']['client_secret'],
        user_agent=self.config['reddit']['user_agent']
        )
        for ext in self.initial_extensions:
            await self.load_extension(ext)
        await self.tree.sync()

    async def on_ready(self):
        print(f'Bot : {self.user}')
        print(f'Guilds : {len(self.guilds)}')
        print('──────────────────────────────────────────')

with open('config.json', encoding='utf-8') as f:
    config = json.load(f)

if __name__ == '__main__':
    with open('config.json', 'r') as f:
        config = json.load(f)
    client = Bot(config)
    client.run(token=config['discord_token'])