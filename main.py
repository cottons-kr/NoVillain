import discord
import os
import sys
from discord.ext import commands

token = open("token", 'r').read()
password = open("password", 'r').read()

whiteList = []
blockword = []
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='./', intents=intents)

def log(content, level=0):
    if level == 0:
        print(f"[INFO] {content}")
    elif level == 1:
        print(f"[ERR] {content}")
    elif level == 2:
        print(f"[IMPORTANT] {content}")

@bot.event
async def on_ready():
    log("BOT START!")
    log(f"Logged in as {bot.user.name}")
    log(f"Bot's ID is {bot.user.id}")
    log(f"The Password is {password}", 2)
    print('='*10)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("올바른 명령어를 입력해주세요")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("권한에러")
    else:
       log(error, 1)

@bot.command()
async def ban(ctx, userId, reason="없음"):
    if not ctx.message.author in whiteList:
        log(f"Not whitelisted member tried to use this bot\nThat member is {ctx.message.author}")
        return 0
    user = bot.get_user(int(userId))
    if user == None:
        log("No such member")
        await ctx.send("없는 멤버입니다")
        return 0
    await ctx.guild.ban(user, reason=reason)
    ctx.send(f"{user.name}(이)가 차단됐습니다.\n사유 : {reason}")
    log(f"{user.name} was banned\nThe reason is {reason}")

@bot.command()
async def unban(ctx, userId):
    if not ctx.message.author in whiteList:
        log(f"Not whitelisted member tried to use this bot\nThat member is {ctx.message.author}")
        return 0
    banlist = await ctx.guild.bans()
    user = bot.get_user(int(userId))
    if user == None:
        log("No such member")
        await ctx.send("없는 멤버입니다")
        return 0
    username = user.name
    usernum = user.discriminator
    for ban_entry in banlist:
        user = ban_entry.user
        if (user.name, user.discriminator) == (username, usernum):
            await ctx.guild.unban(user)
            await ctx.send(f'{user.mention}(이)가 차단 해제됐습니다!')
            log(f"{user.name} was unbanned")
            return 0

@bot.command()
async def banlist(ctx):
    bans = await ctx.guild.bans()
    if len(bans) == 0:
        await ctx.send("차단된 멤버가 없습니다")
        return 0
    loop = [f"{u[1]} ({u[1].id})" for u in bans]
    _list = "\r\n".join([f"[{str(num).zfill(2)}] {data}" for num, data in enumerate(loop, start=1)])
    await ctx.send("<차단리스트>")
    await ctx.send(f"```ini\n{_list}```")
    log("Show banlist")

@bot.command()
async def addwl(ctx, userId, inputpassword):
    user = bot.get_user(int(userId))
    if user == None:
        log("No such member")
        await ctx.send("없는 멤버입니다")
        return 0
    if not inputpassword == password:
        await ctx.send("비밀번호가 올바르지 않습니다")
        log(f"Incorrect password by {user.name}", 2)
        return 0
    whiteList.append(user)
    await ctx.send(f"{user.name}(이)가 화이트리스트에 추가됐습니다")
    log(f"{user.name} was appended at whitelist")

@bot.command()
async def whitelist(ctx):
    if not ctx.message.author in whiteList:
        log(f"Not whitelisted member tried to use this bot\nThat member is {ctx.message.author}")
        return 0
    await ctx.send(whiteList)

@bot.command()
async def smlay(ctx, part, mapid=None, mappw=None, link=None):
    if part == help:
        msg = '''
        등록하는 방법은 다음과 같습니다.
./smlay 파트번호, 맵ID, 복사비번, 유튜브링크(선택)
만약 파트번호가 6, 맵ID가 12345678, 복사비번이 1234, 유튜브링크가 youtu.be/test 라면
./smlay 6 12345678 1234 youtu.be/test 를 입력하면 됩니다.
유튜브 링크가 없으면 입력 안하셔도 됩니다.'''
        dm = bot.get_user(ctx.message.author.id)
        dm.send_message(msg)

bot.run(token)
