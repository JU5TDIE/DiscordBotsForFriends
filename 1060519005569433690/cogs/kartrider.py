import random
import discord
import datetime
from discord.ext import commands
from discord import app_commands

def kart_embed():
    quotes = ["“Goodbyes make you think. They make you realize what you’ve had, what you’ve lost, and what you’ve taken for granted.”", "“The story of life is quicker than the wink of an eye, the story of love is hello and goodbye, until we meet again.”", "If you're brave enough to say goodbye, life will reward you with a new hello.", "Don't cry because it's over. Smile because it happened."]
    embedVar = discord.Embed(title='RIP Kartrider (2004-2023)')
    embedVar.set_image(url='attachment://rip_kartrider.png')
    embedVar.set_footer(text=f"{random.choice(quotes)} Farewell, Kartrider")
    return embedVar

def kart_schedule_embed():
    schedules = ['2023.01.06 > 결제 서비스 종료', '2023.01.12 > 카트라이더 드림(Dream) 프로젝트 페이지 오픈', '2023.02.01 > 카트라이더 환불 신청 페이지 오픈', '2023.03.31 > 카트라이더 서비스 종료']
    kst = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    now = kst.replace(hour=0, minute=0, second=0, microsecond=0)
    for index, schedule in enumerate(schedules):
        date = datetime.datetime.strptime(schedule.split('>')[0].strip(), '%Y.%m.%d')
        if date == now:
            schedule = f'**`{schedule}`**'
        elif date < now:
            schedule = f'~~`{schedule}`~~'
        elif date > now:
            schedule = f'`{schedule}`'
        schedules[index] = schedule
    embedVar = discord.Embed(title='카트라이더 서비스 종료 일정', description='\n'.join(schedules))
    embedVar.set_image(url='attachment://the_end.png')
    return embedVar

class KartRider(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    kart = app_commands.Group(name='kart', description='kartrider 2004-2023 rip')
    
    @kart.command(description='The End')
    async def end(self, interaction: discord.Interaction):
        file = discord.File('./attachments/IMG_4644.jpg', filename='rip_kartrider.png')
        await interaction.response.send_message(file=file, embed=kart_embed())

    @kart.command(description='카트라이더 서비스 종료 일정')
    async def schedule(self, interaction: discord.Interaction):
        file = discord.File('./attachments/IMG_4647.jpg', filename='the_end.png')
        await interaction.response.send_message(file=file, embed=kart_schedule_embed())

async def setup(client):
	await client.add_cog(KartRider(client))