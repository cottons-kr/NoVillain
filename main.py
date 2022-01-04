from logging import warn
import discord
import os
import sys
from discord.ext import commands

token = open("token", 'r').read()

whiteList = []
makers = []
warnning = []
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='./', intents=intents)

ids = [927804798563156028, 927811839335727107] #submit, application
blockWord = open("blockWord", "r", encoding="utf-8").read().split("//")

def log(content, level=0):
    if level == 0:
        print(f"[INFO] {content}")
    elif level == 1:
        print(f"[ERR] {content}")
    elif level == 2:
        print(f"[IMPORTANT] {content}")

def saveBlockWord(list):
    fileContent = ""
    for word in list:
        fileContent += f"{word}//"
    fileContent = fileContent.rstrip("//")
    with open("blockWord", "w", encoding="utf-8") as file:
        file.write(fileContent)

def saveWarnning(list):
    fileContent = ""
    for word in list:
        fileContent += f"{word}//"
    fileContent = fileContent.rstrip("//")
    with open("warnning", "w", encoding="utf-8") as file:
        file.write(fileContent)

@bot.event
async def on_ready():
    log("BOT START!")
    log(f"Logged in as {bot.user.name}")
    log(f"Bot's ID is {bot.user.id}")
    print('='*20)
    whiteList.append(bot.get_user(557927301522915338))
    whiteList.append(bot.get_user(819356866017493052))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("올바른 명령어를 입력해주세요")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("권한에러")

@bot.event
async def on_message(message):
    if "./" in message.content:
        await bot.process_commands(message)
    if message.content in blockWord:
        await message.delete()
        await message.author.send("금지어를 사용하셨습니다! +1 경고 / 3번 경고시 차단됩니다")
        warnning.append(message.author)
        log(f"{message.author} used block word : {message.content}")
    if warnning.count(message.author) >= 3:
        await message.author.ban()
        reason = "금지어 3번 사용"
        message.channel.send(f"{message.author}(이)가 차단됐습니다.\n사유 : {reason}")
        log(f"{message.name} was banned. The reason is {reason}")
        while not message.author in warnning:
            warnning.remove(message.author)

@bot.command()
async def ban(ctx, userId, reason="없음"):
    print(ctx)
    if not ctx.message.author in whiteList:
        log(f"Not whitelisted member tried to use this bot\nThat member is {ctx.message.author}")
        await ctx.message.delete()
        return 0
    user = bot.get_user(int(userId))
    if user == None:
        log("No such member")
        await ctx.send("없는 멤버입니다")
        return 0
    await ctx.guild.ban(user, reason=reason)
    ctx.send(f"{user.name}(이)가 차단됐습니다.\n사유 : {reason}")
    log(f"{user.name} was banned. The reason is {reason}")

@bot.command()
async def unban(ctx, userId):
    if not ctx.message.author in whiteList:
        log(f"Not whitelisted member tried to use this bot. That member is {ctx.message.author}")
        await ctx.message.delete()
        return 0
    banlist = await ctx.guild.bans()
    user = bot.get_user(int(userId))
    if user == None:
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
async def smlay(ctx, part, mapid=None, mappw="없음", link=None, comment="없음"):
    await ctx.message.delete()
    if part == "help":
        msg = '''등록하는 방법은 다음과 같습니다.
```./smlay 파트번호, 맵ID, 복사비번, 유튜브링크```
만약 파트번호가 6, 맵ID가 12345678, 복사비번이 1234, 유튜브링크가 youtu.be/test 라면
```./smlay 6 12345678 1234 youtu.be/test``` 를 입력하면 됩니다.

만약 링크는 있지만 복사비번이 없을땐
```./smlay 6 12345678 없음 youtu.be/test```
이런식으로 입력하시면 됩니다'''
        await ctx.message.author.send(msg)
        return 0
    if not bot.get_user(ctx.message.author.id) in makers:
        await ctx.message.author.send("아직 등록할 수 없습니다")
        return 0
    if int(part) <= 19 or int(part) <= 0:
        await ctx.message.author.send("파트를 확인해주세요")
        return 0
    if mapid == None:
        await ctx.message.author.send("맵ID는 필수입니다")
        return 0
    if link == None:
        await ctx.message.author.send("유튜브 링크를 달아주세요")
        return 0

    msg = f'''**<레이아웃 등록됨 [{ctx.message.author.name}]>**
링크 : {link}
Part #{part}
ID : {mapid}
비밀번호 : {mappw}
**<전하는 말>**
{comment}'''
    submitChannel = bot.get_channel(ids[0])
    await submitChannel.send(msg)
    await ctx.message.author.send("성공적으로 등록됐습니다!")
    log(f"Part #{part} layout submited, Maker : {ctx.message.author.name}")

@bot.command()
async def smdesign(ctx, part, mapid=None, mappw="없음", link=None, comment="없음"):
    await ctx.message.delete()
    if part == "help":
        msg = '''등록하는 방법은 다음과 같습니다.
```./smdesign 파트번호, 맵ID, 복사비번, 유튜브링크```
만약 파트번호가 6, 맵ID가 12345678, 복사비번이 1234, 유튜브링크가 youtu.be/test 라면
```./smdesign 6 12345678 1234 youtu.be/test``` 를 입력하면 됩니다.

만약 링크는 있지만 복사비번이 없을땐
```./smdesign 6 12345678 없음 youtu.be/test```
이런식으로 입력하시면 됩니다
'''
        await ctx.message.author.send(msg)
        return 0
    if not ctx.message.author in makers:
        await ctx.message.author.send("아직 등록할 수 없습니다")
        return 0
    if int(part) <= 19 or int(part) <= 1:
        await ctx.message.author.send("등록할 수 없습니다")
        return 0
    if mapid == None:
        await ctx.message.author.send("맵ID는 필수입니다")
        return 0
    if link == None:
        await ctx.message.author.send("유튜브 링크를 달아주세요")
        return 0
    msg = f'''**<디자인 등록됨 [{ctx.message.author.name}]>**
링크 : {link}
Part #{part}
ID : {mapid}
비밀번호 : {mappw}
**<전하는 말>**
{comment}'''
    submitChannel = bot.get_channel(ids[0])
    await submitChannel.send(msg)
    log(f"Part #{part} design submited, Maker : {ctx.message.author.name}")

@bot.command()
async def app(ctx, type, part, link=None):
    await ctx.message.delete()
    if link == None:
        ctx.message.author.send("유튜브 영상이 필요합니다")
        return 0
    msg = f'''**<{type} 신청함 [{ctx.message.author.name}]>
Part #{part}**
{link}'''
    appChannel = bot.get_channel(ids[1])
    await appChannel.send(msg)
    log(f"{ctx.message.author.name} applied for registration")

@bot.command()
async def cancel(ctx, userId):
    if not ctx.message.author in whiteList:
        log(f"Not whitelisted member tried to use this bot\nThat member is {ctx.message.author}")
        await ctx.message.delete()
        return 0
    member = bot.get_user(int(userId))
    if member == None:
        await ctx.send("없는 멤버입니다")
        return 0
    if not member in makers:
        await ctx.send("Maker가 아닌 멤버입니다")
    makers.remove(member)
    await ctx.send(f"{member.name}는 이제 Maker가 아닙니다")
    log(f"Removed Maker : {member.name}")

@bot.command()
async def submit(ctx, userId):
    if not ctx.message.author in whiteList:
        log(f"Not whitelisted member tried to use this bot\nThat member is {ctx.message.author}")
        await ctx.message.delete()
        return 0
    member = bot.get_user(int(userId))
    if member == None:
        await ctx.send("없는 멤버입니다")
        return 0
    if member in makers:
        await ctx.send("이미 추가되있습니다")
        return 0
    makers.append(member)
    await ctx.send(f"{member.name}이(가) Maker에 추가되었습니다")
    await member.send("이제 등록할 수 있습니다!")
    log(f"New Maker : {member.name}")

@bot.command()
async def maker(ctx):
    if not ctx.message.author in whiteList:
        log(f"Not whitelisted member tried to use this bot\nThat member is {ctx.message.author}")
        await ctx.message.delete()
        return 0
    if len(makers) == 0:
        await ctx.send("Maker가 없습니다")
        return 0
    await ctx.send(makers)
    log("Show maker list")

@bot.command()
async def hello(ctx):
    await ctx.send(f"{ctx.message.author.mention}님, 안녕하세요!")
    log(f"Say hello to {ctx.message.author.name}")

@bot.command()
async def addblock(ctx, word):
    if not ctx.message.author in whiteList:
        log(f"Not whitelisted member tried to use this bot\nThat member is {ctx.message.author}")
        await ctx.message.delete()
        return 0
    blockWord.append(word)
    saveBlockWord(blockWord)
    log(f"New block word : {word}")

@bot.command()
async def rmblock(ctx, word):
    if not ctx.message.author in whiteList:
        log(f"Not whitelisted member tried to use this bot\nThat member is {ctx.message.author}")
        await ctx.message.delete()
        return 0
    blockWord.remove(word)
    saveBlockWord(blockWord)
    log(f"Removed block word : {word}")

@bot.command()
async def blockword(ctx):
    await ctx.message.author.send(blockWord)
    log(f"Show block words to {ctx.message.author.name}")

@bot.command()
async def resetwarnning(ctx, userId):
    member = bot.get_user(int(userId))
    if member == None:
        await ctx.send("없는 멤버입니다")
        return 0
    while not member in warnning:
        warnning.remove(member)

bot.run(token)