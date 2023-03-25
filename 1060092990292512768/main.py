import json
import discord
import requests
from discord.ext import commands
from discord import app_commands

from PIL import Image
from emojify import emojify_image
from typing import Union

class Bot(commands.Bot):
    def __init__(self):
        super().__init__('', intents=discord.Intents.default())

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f'Bot : {self.user}')
        print(f'Guilds : {len(self.guilds)}')
        print('──────────────────────────────────────────')

with open('config.json', encoding='utf-8') as f:
    config = json.load(f)

client = Bot()

emojify = app_commands.Group(name='도트화', description='선택된 사진을 도트화')

async def _emojify(source: Union[discord.Member, discord.User, str], size: int):
    if not isinstance(source, str):
        source = source.display_avatar.url

    def get_emojified_image():
        r = requests.get(source, stream=True)
        image = Image.open(r.raw).convert("RGB")
        res = emojify_image(image, size)

        if size > 14:
            res = f"```{res}```"
        return res

    return await client.loop.run_in_executor(None, get_emojified_image)

@emojify.command(name='프로필', description='선택된 유저의 프로필 사진을 도트화')
@app_commands.describe(member='프로필 사진 도트화할 유저')
@app_commands.describe(size='도트 사이즈 1~44')
@app_commands.rename(member='멤버')
@app_commands.rename(size='사이즈')
async def profile(interaction: discord.Interaction, member: Union[discord.Member, discord.User], size: app_commands.Range[int, 1, 44] = 14):
    result = await _emojify(member, size)
    await interaction.response.send_message(content=result)

@emojify.command(name='링크', description='선택된 링크 사진을 도트화')
@app_commands.describe(link='도트화할 사진 링크')
@app_commands.describe(size='도트 사이즈 1~44')
@app_commands.rename(link='링크')
@app_commands.rename(size='사이즈')
async def link(interaction: discord.Interaction, link: str, size: app_commands.Range[int, 1, 44] = 14):
    result = await _emojify(link, size)
    await interaction.response.send_message(content=result)

client.tree.add_command(emojify)

client.run(config['discord_token'])