import asyncio
import discord
import asyncprawcore
from typing import List, Union
from utils.db import aioDbLite
from discord.ext import commands
from discord import app_commands
from asyncpraw.models import Subreddit

def default_feed(member: discord.Member):
    embedVar = discord.Embed(title='REDDIT FEED')
    embedVar.set_author(name=member, icon_url='https://www.iconpacks.net/icons/2/free-reddit-logo-icon-2436-thumb.png')
    avatarurl = member.avatar.url if member.avatar else member.default_avatar.url
    embedVar.set_thumbnail(url=avatarurl)
    return embedVar

class RedditFeed(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        
    async def fetch_subscribed_subreddits(self, userid: int) -> Union[List[str], None]:
        aiodb = await aioDbLite(self.client.config['db_location'])
        result = await aiodb.select('reddit_subscribed', 'subreddit', userid=userid)
        if result:
            return [subreddit[0] for subreddit in result]
        else:
            return result

    async def fetch_subreddit_top_post(self, subreddit_name: str):
        subreddit: Subreddit = await self.client.reddit.subreddit(subreddit_name)
        try:
            async for post in subreddit.top(limit=1, time_filter='day'):
                return [subreddit, post]
        except asyncprawcore.exceptions.Forbidden:
            pass
        
    @commands.Cog.listener()
    async def on_ready(self):
        aiodb = await aioDbLite(self.client.config['db_location'])
        await aiodb.create('reddit_subscribed', userid='int', subreddit='text')
        print('Reddit feed is ready')

    feed = app_commands.Group(name='feed', description='reddit feed', guild_only=True)

    @feed.command(description='Show top post from each subscribed subreddits')
    async def show(self, interaction: discord.Interaction):
        await interaction.response.send_message(content=f"Loading feed...")
        subreddits = await self.fetch_subscribed_subreddits(interaction.user.id)
        if not subreddits: # empty feed
            return await interaction.edit_original_response(content="Your feed is empty. Use **/feed add** command to fill your empty feed")
        tasks = [self.fetch_subreddit_top_post(subreddit) for subreddit in subreddits]
        posts = await asyncio.gather(*tasks)
        feed_embed = default_feed(interaction.user)
        for post in posts:
            subreddit = post[0]
            post = post[1]
            feed_embed.add_field(name=f'{subreddit.display_name}', value=f'[{post.title}](https://www.reddit.com{post.permalink})', inline=False)
        await interaction.edit_original_response(content="", embed=feed_embed)
            
    @feed.command(description='Add subreddit to feed')
    async def add(self, interaction: discord.Interaction, subreddit_name: str):
        subreddits = await self.fetch_subscribed_subreddits(interaction.user.id)
        if len(subreddits) >= 25: # Too many subreddits; cannot add more than 25 fields in embed
            return await interaction.response.send_message(content="You cannot add more than 25 subreddits", ephemeral=True)
        if subreddit_name in subreddits: # selected subreddit already in user's feed
            return await interaction.response.send_message(content=f"The subreddit(r/{subreddit_name}) is already in your feed", ephemeral=True)
        try:
            result = await self.fetch_subreddit_top_post(subreddit_name) # check if subreddit is available, otherwise it drops 3 different errors
            subreddit: Subreddit = result[0]
            aiodb = await aioDbLite(self.client.config['db_location'])
            await aiodb.add('reddit_subscribed', userid=interaction.user.id, subreddit=subreddit.display_name)
            await interaction.response.send_message(content=f"Loading subreddit(r/{subreddit.display_name})...")
            await subreddit.load()
            feed_embed = default_feed(interaction.user)
            if subreddit.icon_img:
                feed_embed.set_thumbnail(url=subreddit.icon_img)
            else:
                feed_embed.set_thumbnail(url=None)
            feed_embed.add_field(name='INFO', value=f"The subreddit([r/{subreddit.display_name}](https://www.reddit.com/r/{subreddit.display_name})) has been added to your feed", inline=False)
            await interaction.edit_original_response(content="", embed=feed_embed)
        except asyncprawcore.NotFound:
            await interaction.response.send_message(content=f"The subreddit(r/{subreddit_name}) has been banned from reddit", ephemeral=True)
        except asyncprawcore.Redirect:
            await interaction.response.send_message(content=f"The subreddit(r/{subreddit_name}) does not exist", ephemeral=True)
        except asyncprawcore.Forbidden:
            await interaction.response.send_message(content=f"The subreddit(r/{subreddit_name}) is private", ephemeral=True)

    @feed.command(description='Remove subreddit from feed')
    async def remove(self, interaction: discord.Interaction, subreddit_name: str):
        aiodb = await aioDbLite(self.client.config['db_location'])
        await aiodb.remove('reddit_subscribed', subreddit=subreddit_name, userid=interaction.user.id)
        await interaction.response.send_message(content=f"The subreddit(r/{subreddit_name}) has been removed from your feed", ephemeral=True)

    @remove.autocomplete('subreddit_name')
    async def subreddits_autocomplete(self, interaction: discord.Interaction, current: str):
        subreddits = await self.fetch_subscribed_subreddits(interaction.user.id)
        return [app_commands.Choice(name=subreddit, value=subreddit) for subreddit in subreddits]

    @feed.command(description='Clear all subreddits from feed')
    async def clear(self, interaction: discord.Interaction):
        aiodb = await aioDbLite(self.client.config['db_location'])
        await aiodb.remove('reddit_subscribed', userid=interaction.user.id)
        await interaction.response.send_message(content=f"Wiped {interaction.user}'s feed", ephemeral=True)

async def setup(client):
	await client.add_cog(RedditFeed(client))