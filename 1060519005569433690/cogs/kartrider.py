import aiohttp
import random
import discord
import datetime
import json
import zipfile
from discord.ext import commands
from discord import app_commands

letter = '''
안녕하세요, 카트라이더입니다.

2023년 3월 31일, 어느덧 그날이 다가왔습니다.
카트라이더가 라이더님과 함께 해온 소중한 여정에 마침표를 찍게 되었습니다.

라이더 여러분과 함께 달려온 지난 18여 년은
카트라이더 개발팀 모두에게 무엇과도 바꿀 수 없는 소중하고 행복한 기억입니다.

라이더 여러분과 수없이 많은 계절을 함께 보내며
매 순간 벅찬 마음으로 모두에게 사랑받는 게임이 되기 위한 도전을 멈추지 않았습니다.
라이더 여러분이 보내주셨던 따뜻한 관심, 따끔한 충고 그 모두가
개발진의 치열한 고민과 쉽 없는 도전의 원동력이 되어주었습니다.
라이더 여러분께 마음 깊이 감사드리며 함께한 시간 영광이었습니다.

인연의 끝은 언제나 아쉬움으로 가득하지만, 그 과정 속 의미를 되새기고 안녕을 건네고자 합니다.
카트라이더와 함께한 시간이 라이더 여러분께 잊을 수 없는 행복한 추억이었기를 바라며, 
개발팀 또한 라이더 여러분들과 함께 한 모든 순간을 가슴 깊이 간직하겠습니다.

끝이 아닌 새로운 시작을 향해 달려 나가는 카트라이더의 미래에도
한없이 따뜻한 관심과 성원을 부탁드립니다.

감사합니다.

사랑과 존경을 가득 담아,
카트라이더 개발팀 드림
'''

def kartrider_the_end_embed():
    quotes = ["“Goodbyes make you think. They make you realize what you’ve had, what you’ve lost, and what you’ve taken for granted.”", "“The story of life is quicker than the wink of an eye, the story of love is hello and goodbye, until we meet again.”", "If you're brave enough to say goodbye, life will reward you with a new hello.", "Don't cry because it's over. Smile because it happened."]
    embedVar = discord.Embed(title='RIP Kartrider (2004-2023)')
    embedVar.set_image(url='attachment://rip_kartrider.png')
    embedVar.set_footer(text=f"{random.choice(quotes)} Farewell, Kartrider")
    return embedVar

def kartrider_schedule_embed():
    schedules = ['2023.01.06 > 결제 서비스 종료', '2023.01.12 > 카트라이더 드림(Dream) 프로젝트 페이지 오픈', '2023.02.01 > 카트라이더 환불 신청 페이지 오픈', '2023.03.31 > 카트라이더 서비스 종료']
    kst = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    now = kst.replace(hour=0, minute=0, second=0, microsecond=0)
    for index, schedule in enumerate(schedules):
        date = datetime.datetime.strptime(schedule.split('>')[0].strip(), '%Y.%m.%d')
        if date == now:
            schedule = f'**`{schedule}`**'
        elif date < now:
            schedule = f'~~`{schedule}`~~ (<t:{int(datetime.datetime.timestamp(date))}:R>)'
        elif date > now:
            schedule = f'`{schedule}` (<t:{int(datetime.datetime.timestamp(date))}:R>)'
        schedules[index] = schedule
    embedVar = discord.Embed(title='카트라이더 서비스 종료 일정', description='\n'.join(schedules))
    embedVar.set_image(url='attachment://the_end.png')
    return embedVar

def kartrider_kart_embed(item):
    embedVar = discord.Embed(title=item['name'])
    embedVar.set_image(url=f"attachment://{item['id']}.png")
    return embedVar

async def get_metadata():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://static.api.nexon.co.kr/kart/latest/metadata.zip') as response:
            if response.status == 200:
                with open('metadata.zip', "wb") as f:
                    f.write(await response.read())
            else:
                print(f'Error: {response.status}')

class KartRider(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.metadata = {}
        if not zipfile.is_zipfile('metadata.zip'):
            await get_metadata()
        with zipfile.ZipFile('metadata.zip', 'r') as z:
            for filename in z.namelist():
                if filename.endswith('.json') and filename not in ['gameType.json', 'flyingPet.json', 'pet.json']: # TODO remove these json files if they are ready
                    with z.open(filename) as f:
                        self.metadata[filename.split('.json')[0]] = json.loads(f.read().decode('utf-8'))
        print('Kartrider is ready')

    kartrider = app_commands.Group(name='kartrider', description='kartrider 2004-2023 rip')
    
    @kartrider.command(description='The End')
    async def end(self, interaction: discord.Interaction):
        file = discord.File('./attachments/IMG_4644.jpg', filename='rip_kartrider.png')
        await interaction.response.send_message(file=file, embed=kartrider_the_end_embed())

    @kartrider.command(description='카트라이더 서비스 종료 일정')
    async def schedule(self, interaction: discord.Interaction):
        file = discord.File('./attachments/IMG_4647.jpg', filename='the_end.png')
        await interaction.response.send_message(file=file, embed=kartrider_schedule_embed())

    @kartrider.command(description='카트라이더 마지막 편지')
    async def letter(self, interaction: discord.Interaction):
        file = discord.File('./attachments/6940049224801243763.jpg', filename='letter.png')
        embedVar = discord.Embed(description=letter)
        embedVar.set_image(url='attachment://letter.png')
        await interaction.response.send_message(file=file, embed=embedVar)

    @kartrider.command(description='카트라이더 메타데이터 검색')
    @app_commands.rename(search_type='type')
    @app_commands.rename(search_name='name')
    async def search(self, interaction: discord.Interaction, search_type: str, search_name: str):
        if not search_type in self.metadata.keys():
            raise 
        if not [item for item in self.metadata[search_type] if item['name'] == search_name]:
            raise
        item = next(item for item in self.metadata[search_type] if item['name'] == search_name)
        with zipfile.ZipFile('metadata.zip', 'r') as z:
            try:
                with z.open(f"{search_type}/{item['id']}.png") as f:
                    file = discord.File(f, filename=f"{item['id']}.png")
            except KeyError: # image not found
                file = discord.File('./attachments/invisible.png', filename=f"{item['id']}.png")
        await interaction.response.send_message(file=file, embed=kartrider_kart_embed(item))

    @search.autocomplete('search_type')
    async def search_type_autocomplete(self, interaction: discord.Interaction, current: str):
        return [app_commands.Choice(name=data_type, value=data_type) for data_type in self.metadata.keys()]

    @search.autocomplete('search_name')
    async def search_name_autocomplete(self, interaction: discord.Interaction, current: str):
        if interaction.namespace.type and self.metadata.get(interaction.namespace.type):
            return [
                app_commands.Choice(name=item['name'], value=item['name'])
                for item in self.metadata[interaction.namespace.type] if current.lower() in item['name'].lower()
            ][:25]
        else:
            return []

async def setup(client):
	await client.add_cog(KartRider(client))