import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import os

# 봇 설정
TOKEN = "access_token"
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()  # 슬래시 명령어 동기화
        print(f"✅ {len(synced)}개의 명령어가 동기화됨")
    except Exception as e:
        print(f"❌ 명령어 동기화 중 오류 발생: {e}")

# ✅ 특정 사용자 ID만 관리자 권한 부여
ADMIN_USERS = [1026461818052411452, 1107153315239833711]  # 여기에 관리자 ID 입력

# ✅ 박제 목록 저장 (임시 데이터)
pinned_messages = {
    "큐브조합": [],
    "로블록스": []
}

# ✅ 봇이 준비되었을 때 실행
@bot.event
async def on_ready():
    await bot.tree.sync()  # 슬래시 명령어 동기화
    print(f"✅ {bot.user} 온라인!")

# ✅ 박제 추가 명령어
@bot.tree.command(name="박제", description="특정 카테고리에 메시지를 박제합니다.")
@app_commands.describe(category="박제할 카테고리 (큐브조합/로블록스)", content="박제할 내용")
async def 박제(interaction: discord.Interaction, category: str, content: str):
    if category not in pinned_messages:
        await interaction.response.send_message("❌ 존재하지 않는 카테고리입니다! (`큐브조합`, `로블록스` 중 선택)", ephemeral=True)
        return

    pinned_messages[category].append(content)
    await interaction.response.send_message(f"✅ `{category}` 카테고리에 박제 완료!")

# ✅ 박제 목록 조회 명령어
@bot.tree.command(name="박제목록", description="선택한 카테고리의 박제 목록을 확인합니다.")
@app_commands.describe(category="확인할 카테고리 (큐브조합/로블록스)")
async def 박제목록(interaction: discord.Interaction, category: str):
    if category not in pinned_messages:
        await interaction.response.send_message("❌ 존재하지 않는 카테고리입니다! (`큐브조합`, `로블록스` 중 선택)", ephemeral=True)
        return

    if not pinned_messages[category]:
        await interaction.response.send_message(f"📂 `{category}` 카테고리에 저장된 박제가 없습니다.")
        return

    embed = discord.Embed(title=f"📌 {category} 박제 목록", color=discord.Color.blue())
    for idx, msg in enumerate(pinned_messages[category], 1):
        embed.add_field(name=f"{idx}.", value=msg, inline=False)

    await interaction.response.send_message(embed=embed)

# ✅ 박제 삭제 명령어 (특정 ID만 가능)
@bot.tree.command(name="박제삭제", description="특정 카테고리의 박제를 삭제합니다. (특정 관리자만 가능)")
@app_commands.describe(category="삭제할 카테고리 (큐브조합/로블록스)", index="삭제할 박제 번호")
async def 박제삭제(interaction: discord.Interaction, category: str, index: int):
    if interaction.user.id not in ADMIN_USERS:
        await interaction.response.send_message("❌ 당신은 이 명령어를 실행할 권한이 없습니다!", ephemeral=True)
        return

    if category not in pinned_messages:
        await interaction.response.send_message("❌ 존재하지 않는 카테고리입니다!", ephemeral=True)
        return
    
    if index <= 0 or index > len(pinned_messages[category]):
        await interaction.response.send_message("❌ 잘못된 인덱스입니다!", ephemeral=True)
        return

    deleted_msg = pinned_messages[category].pop(index - 1)
    await interaction.response.send_message(f"🗑 `{category}`에서 `{deleted_msg}` 삭제 완료!")

# ✅ 봇이 준비되었을 때 실행 (on_ready 통합)
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()  # 슬래시 명령어 동기화
        print(f"✅ {len(synced)}개의 명령어가 동기화됨")
    except Exception as e:
        print(f"❌ 슬래시 명령어 동기화 오류: {e}")

    # 🔹 봇이 몇 개의 서버에서 사용 중인지 표시
    activity = discord.Game(name=f"{len(bot.guilds)}개의 서버에서 사용 중! 🚀")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"✅ {bot.user} 온라인! 현재 {len(bot.guilds)}개의 서버에서 사용 중!")

# ✅ 새로운 서버에 추가될 때 상태 메시지 업데이트
@bot.event
async def on_guild_join(guild):
    activity = discord.Game(name=f"{len(bot.guilds)}개의 서버에서 사용 중! 🚀")
    await bot.change_presence(activity=activity)

# ✅ 서버에서 나가면 상태 메시지 업데이트
@bot.event
async def on_guild_remove(guild):
    activity = discord.Game(name=f"{len(bot.guilds)}개의 서버에서 사용 중! 🚀")
    await bot.change_presence(activity=activity)




# ✅ 로블록스 유저 조회 명령어
@bot.tree.command(name="로블록스유저찾기", description="닉네임을 입력하면 해당 유저의 프로필 링크를 제공합니다.")
@app_commands.describe(username="찾을 로블록스 닉네임")
async def 로블록스유저찾기(interaction: discord.Interaction, username: str):
    url = "https://users.roblox.com/v1/usernames/users"
    payload = {"usernames": [username], "excludeBannedUsers": True}
    headers = {"Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status != 200:
                await interaction.response.send_message("❌ 로블록스 API 요청 실패! 다시 시도해주세요.", ephemeral=True)
                return
            
            data = await response.json()
            if not data["data"]:
                await interaction.response.send_message("❌ 해당 닉네임의 사용자를 찾을 수 없습니다.", ephemeral=True)
                return
            
            user_id = data["data"][0]["id"]
            profile_link = f"https://www.roblox.com/users/{user_id}/profile"
            await interaction.response.send_message(f"🔍 `{username}`님의 프로필: {profile_link}")


# ✅ 봇 실행
access_token = os.environ["BOT_TOKEN"]
bot.run(TOKEN)
