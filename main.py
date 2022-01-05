import discord
import os
import sys
from datetime import datetime
from discord.ext import commands

token = open("token", 'r').read()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='./', intents=intents)

def log(content, level=0):
    time = datetime.now()
    if level == 0:
        type = "INFO"
    elif level == 1:
        type = "ERROR"
    elif level == 2:
        type = "IMPORTANT"
    elif level == 3:
        type = "WARN"
    print(f"[{time.strftime('%H:%M:%S')}] [{type}] {content}")

def saveAsFile(name, list):
    fileContent = ""
    for word in list:
        fileContent += f"{word}//"
    fileContent = fileContent.rstrip("//")
    with open(name, "w", encoding="utf-8") as file:
        file.write(fileContent)
    log(f"{name} saved")

def loadFromFile(name):
    list = []
    content = open(name, 'r', encoding="utf-8").read().split("//")
    log(f"{name} loaded")
    for id in content:
        list.append(int(id))
    return list

@bot.event
async def on_ready():
    global blockWord, whiteList, makers, warnning, channels
    print("<Seeyou Bot Runner v1.0>")
    date = datetime.now()
    print(f"Start running at [{date.strftime('%B, %d / %Y')}]")
    log("Loading data...")
    if os.path.isfile("blockWord"):
        blockWord = open("blockWord", "r", encoding="utf-8").read().split("//")
    else:
        blockWord = []
    if os.path.isfile("whiteList"):
       whiteList =  loadFromFile("whiteList")
    else:
        log("No whitelist. Is it okay?", 3)
        whiteList = []
    if os.path.isfile("makers"):
        makers = loadFromFile("makers")
    else:
        makers = []
    if os.path.isfile("warnning"):
        warnning = loadFromFile("warnning")
    else:
        warnning = []
    if os.path.isfile("channels"):
        channels = []
        ids = loadFromFile("channels") #submit, application, main
        for id in ids:
            channels.append(bot.get_channel(int(id)))
        if len(channels) < 3:
            log(f"This bot needs 3 channels, Detected channels : {len(channels)}", 1)
            sys.exit(1)
    else:
        log("Cant load the channel IDs!", 1)
        sys.exit(1)
    log("BOT START!")
    log(f"Logged in as {bot.user.name}")
    log(f"Bot's ID is {bot.user.id}")
    print('='*20)

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
        warnning.append(message.author.id)
        log(f"{message.author} used block word : {message.content}")
    if warnning.count(message.author.id) >= 3:
        await message.author.ban()
        reason = "금지어 3번 사용"
        await channels[2].send(f"{message.author.name}(이)가 차단됐습니다.\n사유 : {reason}")
        log(f"{message.name} was banned. The reason is {reason}")
        while message.author.id in warnning:
            warnning.remove(message.author.id)

@bot.command()
async def ban(ctx, userId, reason="없음"):
    print(ctx)
    if not ctx.message.author.id in whiteList:
        log(f"Not whitelisted member tried to use this bot\nThat member is {ctx.message.author}")
        await ctx.message.delete()
        return 0
    user = bot.get_user(int(userId))
    if user == None:
        log("No such member")
        await ctx.send("없는 멤버입니다")
        return 0
    await ctx.guild.ban(user, reason=reason)
    await ctx.send(f"{user.name}(이)가 차단됐습니다.\n사유 : {reason}")
    await channels[2].send(f"{user.name}(이)가 차단됐습니다.\n사유 : {reason}")
    log(f"{user.name} was banned. The reason is {reason}")

@bot.command()
async def unban(ctx, userId):
    if not ctx.message.author.id in whiteList:
        log(f"Not whitelisted member tried to use this bot. That member is {ctx.message.author}")
        await ctx.message.delete()
        return 0
    banlist = await ctx.guild.bans()
    member = bot.get_user(int(userId))
    if member == None:
        await ctx.send("없는 멤버입니다")
        return 0
    username = member.name
    usernum = member.discriminator
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
    print(ctx.message.author.id)
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
    if not ctx.message.author.id in makers:
        await ctx.message.author.send("아직 등록할 수 없습니다")
        return 0
    if int(part) >= 19 or int(part) <= 0:
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
    await channels[0].send(msg)
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
    if not ctx.message.author.id in makers:
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
    await channels[0].send(msg)
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
    await channels[1].send(msg)
    log(f"{ctx.message.author.name} applied for registration")

@bot.command()
async def cancel(ctx, userId):
    if not ctx.message.author.id in whiteList:
        log(f"Not whitelisted member tried to use this bot\nThat member is {ctx.message.author}")
        await ctx.message.delete()
        return 0
    member = bot.get_user(int(userId))
    if member == None:
        await ctx.send("없는 멤버입니다")
        return 0
    if not userId in makers:
        await ctx.send("Maker가 아닌 멤버입니다")
    makers.remove(userId)
    await ctx.send(f"{member.name}는 이제 Maker가 아닙니다")
    await member.send("Maker에서 제거되셨습니다")
    log(f"Removed Maker : {member.name}")
    saveAsFile("makers", makers)

@bot.command()
async def submit(ctx, userId):
    if not ctx.message.author.id in whiteList:
        log(f"Not whitelisted member tried to use this bot\nThat member is {ctx.message.author}")
        await ctx.message.delete()
        return 0
    member = bot.get_user(int(userId))
    if member == None:
        await ctx.send("없는 멤버입니다")
        return 0
    if userId in makers:
        await ctx.send("이미 Maker 입니다")
        return 0
    makers.append(userId)
    await ctx.send(f"{member.name}이(가) Maker에 추가됐습니다")
    await member.send("Maker가 되셨습니다!")
    log(f"New Maker : {member.name}")
    saveAsFile("makers", makers)

@bot.command()
async def maker(ctx):
    if not ctx.message.author.id in whiteList:
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
    if not ctx.message.author.id in whiteList:
        log(f"Not whitelisted member tried to use this bot\nThat member is {ctx.message.author}")
        await ctx.message.delete()
        return 0
    if not word in blockWord:
        await ctx.send(f"{word}은(는) 이제 금지어 입니다")
        blockWord.append(word)
        saveAsFile("blockWord", blockWord)
        log(f"New block word : {word}")
    else:
        await ctx.send("중복된 단어입니다")

@bot.command()
async def rmblock(ctx, word):
    if not ctx.message.author.id in whiteList:
        log(f"Not whitelisted member tried to use this bot\nThat member is {ctx.message.author}")
        await ctx.message.delete()
        return 0
    if word in blockWord:
        blockWord.remove(word)
        saveAsFile("blockWord", blockWord)
        log(f"Removed block word : {word}")
        await ctx.send(f"{word}은(는) 이제 금지어가 아닙니다")
    else:
        await ctx.send("금지어가 아닙니다")

@bot.command()
async def blockword(ctx):
    if len(blockWord) != 0:
        await ctx.message.author.send(blockWord)
    else:
        await ctx.message.author.send("금지어가 없습니다")
    log(f"Show block words to {ctx.message.author.name}")

@bot.command()
async def resetwarning(ctx, userId):
    if not ctx.message.author.id in whiteList:
        log(f"Not whitelisted member tried to use this bot\nThat member is {ctx.message.author}")
        await ctx.message.delete()
        return 0
    member = bot.get_user(int(userId))
    if member == None:
        await ctx.send("없는 멤버입니다")
        return 0
    while userId in warnning:
        warnning.remove(userId)
    log(f"Removed warning : {member.name}", 3)
    await ctx.send(f"{member.name}의 경고를 삭제했습니다")
    
@bot.command()
async def how(ctx):
    await ctx.message.delete()
    msg = '''
    **For everone**
./banlist : 차단리스트 보기
./hello : 인사받기
./app (타입) (파트) (유튜브링크) : Maker 신청하기
 예) ./app 레이 5 youtu.be/test
./blockword :  금지어 확인(욕설주의)
    
**For Maker**
./smlay : ./smlay help로 자세하게 확인가능
./smdesign : ./smdesign help로 자세하게 확인가능
    
**For whitelist**
안알려줌'''
    await ctx.message.author.send(msg)
    log(f"Show help to {ctx.message.author.name}")

bot.run(token)