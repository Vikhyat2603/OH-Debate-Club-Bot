import discord
import random
from socket import gethostname
import traceback
import os

client = discord.Client()

########################################

rules = {'rule1': 'sample rule 1 text',
         'rule2': 'sample rule 2 text',
         'rule3': 'sample rule 3 text',
         'rule4': 'sample rule 4 text'}

allRulesList = [f'-> {ruleNum} : {rule}' for ruleNum, rule in rules.items()]
allRules = 'All Rules:\n' + '\n'.join(allRulesList)

welcomeMessage = '''Thank you for joining Openhouse Debate Club on Discord, we are so excited to have you on board!
Don’t worry if the new system seems challenging, we are here to help. All the channels here are like different group chats where you can discuss anything you want (channel=chat). Our announcements page will show you the debates you can sign up for, with instructions on signing up. You will immediately be placed into your team. Introduce yourself to your teammates and get ready to battle it out in your debate! Motions and links for your debate will be sent to you on the channel itself.
Please feel free to message us if you are facing any difficulties. Until then, choose to be better :)'''

debateFormatInfo = '''Hello users,
We are following the -- debate format
You can read about this here : <link>'''

availableIDs = set(list(range(1, 1000)))
debateLists = {}
openIDs = set()

debugMode = (gethostname() == 'VKSN-Desktop')

if debugMode:
    botToken, guildID = open('DCbotInfo.txt', 'r').readlines()
    guildID = int(guildID)
else:
    botToken = str(os.environ.get('BOT_TOKEN'))
    guildID = int(os.environ.get('GUILD_ID'))

async def getDebateLists(guild):
    expChannel = discord.utils.get(guild.channels, name='experiments')
    async for msg in expChannel.history(limit=100, oldest_first=False):
        if (msg.author.id == client.user.id) and (msg.content.startswith('<log>')):             
            return eval(msg.content[5:])
    return dict()

despace = lambda s: s.replace(' ', '')
commandPrefix = '!'

########################################
# Log an error message and print if debugMode is on
async def logError(myText):
    expChannel = discord.utils.get(ohGuild.channels, name=f'experiments')
    if debugMode:
        print(str(myText))
    await expChannel.send('<@!693797662960386069> **Log**: ' + str(myText))

# Greet new users on DM
@client.event
async def on_member_join(member):
    try:
        await member.create_dm()
        await member.dm_channel.send(f'Hi {member.name}, welcome to the **Openhouse Debate Club** Server!')
        await member.dm_channel.send(welcomeMessage)
    except Exception as e:
        await logError(f'Member join : {traceback.format_exc()}')

# Fetch a number from text
async def fetchNumber(message, text):
    if text.isdigit():
        return text
    await message.channel.send(f'\'{text}\' is an invalid number')

# Informs me when bot comes online
@client.event
async def on_ready():
    try:
        global availableIDs, openIDs, debateLists, ohGuild
        
        ohGuild = client.get_guild(guildID)
        expChannel = discord.utils.get(ohGuild.channels, name='experiments')
        await logError('Bot is Online')
        
        debateLists = await getDebateLists(ohGuild)
        openIDs = set(debateLists.keys())
        availableIDs = availableIDs.difference(set(map(int, openIDs)))
        
    except Exception as e:
        await logError(traceback.format_exc())
    
# Respond to messages
@client.event
async def on_message(message):
    try:
        global rules, availableIDs, openIDs, debateLists
        
        text = message.content
        author = message.author
        authorStr = str(author)
        authorID = author.id
        guild = message.guild
        
        if guild is not None:
            expChannel = discord.utils.get(guild.channels, name='experiments')

        # Let Vikhyat debug code
        if (authorStr == 'Vikhyat#5088'):
            if text.startswith('!debug'):
                code = text[6:]
                try:
                    await message.channel.send(str(eval(code)))
                except Exception:
                    await logError(traceback.format_exc())

            elif text.startswith('!exec'):
                code = text[6:]
                try:
                    await message.channel.send(str(exec(code)))
                except Exception:
                    await logError(traceback.format_exc())

            elif text.startswith('!clear'):
                await expChannel.send('<log>{}')
                await message.channel.send(f'Emptied debateLists')

            elif text.startswith('!check'):
                await message.channel.send(await getDebateLists(guild))

        # Pass queries to the queries channel
        if text.startswith('!query'):
            query = text[6:]
            queryMessage = ('-' * 80) + f'\nUser : {authorStr}\nQuery : {query}'
            queryChannel = discord.utils.get(guild.channels, name='queries')
            await queryChannel.send(queryMessage)
            await message.channel.send('Sent:\n' + queryMessage)
            return

        text = despace(text.lower())

        # Check for command prefix
        if not text.startswith(commandPrefix):
            return

        # Remove command prefix
        text = text[len(commandPrefix):]
        if text in ['hello', 'hi', 'hey']:
            await message.channel.send(f'Hello there, {author}!')
            return

        if text == 'joke':
            joke = random.choice(open(r'assets\jokes.txt', 'r').readlines()).strip()
            await message.channel.send(joke)
            return

        ############################################################
        
        # State debate format details
        if text == 'debateformat':
            await message.channel.send(debateFormatInfo)
            return

        # State Rules
        if text.startswith('rule'):
            if (text in rules):
                rule = rules[text]
                await message.channel.send(f'->{text}:{rule}')
            elif text in ['rule', 'rules', 'ruleall', 'rulesall']:
                allRulesList = [f'-> {ruleNum} : {rule}' for ruleNum, rule in rules.items()]
                allRules = 'All Rules:\n' + '\n'.join(allRulesList)
                await message.channel.send(allRules)
            else:
                await message.channel.send("Rule does not exist")
            return

        ############################################################
        if guild is None:
            return
        
        # Start debate with fixed max capacity
        if text.startswith('debatewith'):

            # Ensure author has 'Moderator' role
            isMod = discord.utils.get(author.roles, name="Moderator")
            if not isMod:
                await message.channel.send(f'Only server moderators role can start a debate')
                return

            # Fetch debate max capacity and ignore time
            sub = text[10:]
            i = 0
            maxCapStr = ''
            while (i < len(sub)) and sub[i].isdigit():
                maxCapStr += sub[i]
                i += 1

            if not maxCapStr.isdigit():
                await message.channel.send(f'\'{text}\' is an invalid number')
                return

            maxCapacity = int(maxCapStr)
            # Initialise debate details
            debateID = str(min(availableIDs))
            availableIDs.remove(int(debateID))
            debateLists[debateID] = {'nMembers': 0,
                                     'for': [],
                                     'against': [],
                                     'modID': None,
                                     'max': maxCapacity}
            
            # Create roles : for, against and mod
            forRole = await guild.create_role(name=f'Debate {debateID} : For')
            againstRole = await guild.create_role(name=f'Debate {debateID} : Against')
            modRole = await guild.create_role(name=f'Debate {debateID} : Mod')

            # Create category and channels
            category = await guild.create_category(f'Debate {debateID}')

            forChannel = await guild.create_text_channel(f'debate-{debateID}-for', category=category)
            againstChannel = await guild.create_text_channel(f'debate-{debateID}-against', category=category)
            generalChannel = await guild.create_text_channel(f'debate-{debateID}-general', category=category)
            voiceChannel = await guild.create_voice_channel(f'debate-{debateID}-voice', category=category)

            # Restrict Channels according to roles
            channels = [forChannel, againstChannel, generalChannel]
            roles = [forRole, againstRole, modRole]

            everyoneRole = discord.utils.get(guild.roles, name="@everyone")

            for channel in channels:
                await channel.set_permissions(everyoneRole, view_channel=False)

            for role in roles:
                await generalChannel.set_permissions(role, view_channel=True)

            await forChannel.set_permissions(forRole, view_channel=True)
            await againstChannel.set_permissions(againstRole, view_channel=True)

            openIDs.add(debateID)
            myMsg = await message.channel.send(f'Started debate **{debateID}** with max. {maxCapacity} people\
                    \nWrite *!add me {debateID}*  to be added, or *!moderate {debateID}*  to moderate!')

            if not debugMode:
                dmodChannel = discord.utils.get(guild.channels, name=f'debate-moderators')
                await dmodChannel.send('Knock Knock. A Debate is about to Happen. Anyone willing to Moderate?')

        # Add participant to debate
        elif text.startswith('addme'):

            # Ensure debate ID is valid
            debateID = await fetchNumber(message, text[5:])
            if debateID is None:
                return

            # Ensure debate <ID> is open
            if debateID not in openIDs:
                await message.channel.send(f'Sorry {authorStr}, debate {debateID} is not open')
                return

            debateList = debateLists[debateID]
            debateModID = debateList['modID']
            maxCapacity = debateList['max']
            forIDs = debateList['for']
            againstIDs = debateList['against']

            if debateList['nMembers'] == maxCapacity:
                await message.channel.send(f'Sorry {authorStr}, debate **{debateID}** has reached max capacity ({maxCapacity})')
                return

            if authorID in (forIDs + againstIDs):
                await message.channel.send(f'User {authorStr} is already in debate {debateID}')
                return

            if authorID == debateModID:
                await message.channel.send(f'User {authorStr} is the moderator for debate {debateID}, cannot be a participant too')
                return

            # Choose a random stance
            half = maxCapacity // 2
            stance = ''
            randomStance = 'Against' if random.randint(0, 1) else 'For'

            if maxCapacity % 2 == 0:
                if len(forIDs) == half:
                    stance = 'Against'
                elif len(againstIDs) == half:
                    stance = 'For'
                else:
                    stance = randomStance
            else:
                if len(forIDs) == half:
                    if len(againstIDs) == half:
                        stance = randomStance
                    else:
                        stance = 'Against'
                elif len(againstIDs) == half:
                    stance = 'For'
                else:
                    stance = randomStance

            # Assign role and stance
            if stance == 'For':
                forIDs.append(authorID)
                forRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : For')
                await author.add_roles(forRole)
            else:
                againstIDs.append(authorID)
                againstRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : Against')
                await author.add_roles(againstRole)

            debateList['nMembers'] += 1

            await message.channel.send(f'{authorStr} was assigned stance **\'{stance}\'** for debate **{debateID}**')

        # Add moderator to debate
        elif text.startswith('moderate'):

            # Ensure debate ID is valid
            debateID = await fetchNumber(message, text[8:])
            if debateID is None:
                return

            # Ensure debate <ID> is open
            if debateID not in openIDs:
                await message.channel.send(f'Sorry {authorStr}, debate {debateID} is not open')
                return

            debateList = debateLists[debateID]
            debateModID = debateList['modID']
            debateMemberIDs = debateList['for'] + debateList['against']

            # Ensure author is not a participant
            if authorID in debateMemberIDs:
                await message.channel.send(f'User {authorStr} is a participant in debate {debateID}, cannot be a moderator too')
                return

            # Ensure author has 'Debate Moderator' role
            isDebMod = discord.utils.get(author.roles, name="Debate Moderator")
            if not isDebMod:
                await message.channel.send(f'User {authorStr} does not have the role \'Debate Moderator\'')
                return

            # Ensure debate <ID> does not already have mod
            if debateModID is not None:
                await message.channel.send(f'Sorry user {authorStr}, debate {debateID} already has moderator')
                return

            # Assign mod role to author
            debateList['modID'] = authorID

            modRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : Mod')
            await author.add_roles(modRole)

            await message.channel.send(f'Added {authorStr} as moderator to debate {debateID}')

        # Balance stances for debate
        elif text.startswith('balance'):

            # Ensure debate ID is valid
            debateID = await fetchNumber(message, text[7:])
            if debateID is None:
                return

            # Ensure debate <ID> is open
            if debateID not in openIDs:
                await message.channel.send(f'Debate {debateID} is not open')
                return

            debateList = debateLists[debateID]
            debateModID = debateList['modID']

            # Ensure only 'Moderator' or debate's moderator can balance debate
            isMod = discord.utils.get(author.roles, name="Moderator")
            if (not isMod):# and (authorID != debateModID):
                #or the debate moderator
                await message.channel.send(f'Only server moderators can balance the stances')
                return

            # Split members into 2 stances
            memberIDs = debateList['for'] + debateList['against']
            random.shuffle(memberIDs)
            mid = len(memberIDs) // 2
            sections = [memberIDs[:mid], memberIDs[mid:]]
            random.shuffle(sections)

            # Remove old stance roles
            forRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : For')
            againstRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : Against')

            for userID in debateList['for']:
                user = guild.get_member(userID)
                await user.remove_roles(forRole)

            for userID in debateList['against']:
                user = guild.get_member(userID)
                await user.remove_roles(againstRole)

            # Assign new stance roles
            debateList['for'] = sections[0]
            debateList['against'] = sections[1]

            for userID in debateList['for']:
                user = guild.get_member(userID)
                await user.add_roles(forRole)
                await message.channel.send(f'{str(user)} was assigned stance **\'For\'** for debate **{debateID}**')

            for userID in debateList['against']:
                user = guild.get_member(userID)
                await user.add_roles(againstRole)
                await message.channel.send(f'{str(user)} was assigned stance **\'Against\'** for debate **{debateID}**')

            await message.channel.send(f'Debate {debateID} stances balanced')

            memberIDs = debateList['for'] + debateList['against']
            membersStr = list(map(lambda userID : str(guild.get_member(userID)), memberIDs))
            maxCapacity = debateList['max']
            nMembers = debateList['nMembers']
            mod = str(guild.get_member(debateList['modID']))

            await message.channel.send(f'Debate {debateID} ({nMembers}/{maxCapacity}) | Mod: {mod} | Members : {membersStr}')

        # Remove participant/moderator from debate
        elif text.startswith('remove'):
            post = text[6:]
            parts = post.split('<')
            num = parts[0].strip()
            memberID = int(parts[1][2:-1])

            if num.isdigit():
                debateID = num
            else:
                await message.channel.send(f'\'{num}\' is an invalid number')
                return

            if debateID not in openIDs:
                await message.channel.send(f'Debate {debateID} is not open')
                return

            debateList = debateLists[debateID]
            debateModID = debateList['modID']

            # Ensure only 'Moderator' or debate moderator can remove members
            isMod = discord.utils.get(author.roles, name="Moderator")
            if (not isMod):# and (authorID != debateModID):
                #or the debate moderator
                await message.channel.send(f'Only server moderators can remove members')
                return

            forIDs = debateList['for']
            againstIDs = debateList['against']

            if memberID in forIDs:
                member = guild.get_member(memberID)
                forRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : For')
                debateList['for'].remove(memberID)
                debateList['nMembers'] -= 1

                await member.remove_roles(forRole)
                await message.channel.send(f'Removed {str(member)} from debate {debateID}')

            elif memberID in againstIDs:
                member = guild.get_member(memberID)
                againstRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : Against')
                debateList['against'].remove(memberID)
                debateList['nMembers'] -= 1

                await member.remove_roles(againstRole)
                await message.channel.send(f'Removed {str(member)} from debate {debateID}')

            # Remove mod role from author
            elif memberID == debateModID:
                debateList['mod'] = None
                modRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : Mod')
                await author.remove_roles(modRole)
                await message.channel.send(f'Removed moderator {authorStr} from debate {debateID}')

            else:
                await message.channel.send(f'Member not found in debate')

        # Close debate
        elif text.startswith('close'):

            # Ensure debate ID is valid
            debateID = await fetchNumber(message, text[5:])
            if debateID is None:
                return

            # Ensure debate <ID> is open
            if debateID not in openIDs:
                await message.channel.send(f'Debate {debateID} is not open')
                return

            debateList = debateLists[debateID]
            del debateLists[debateID]
            openIDs.remove(debateID)
            
            debateModID = debateList['modID']

            # Ensure only 'Moderator' or debate moderator can close the debate
            isMod = discord.utils.get(author.roles, name="Moderator")
            if (not isMod):# and (authorID != debateModID):
                #or the debate moderator
                await message.channel.send(f'Only server moderators can close the debate')
                return

            # Delete category and channels
            forChannel = discord.utils.get(guild.channels, name=f'debate-{debateID}-for')
            againstChannel = discord.utils.get(guild.channels, name=f'debate-{debateID}-against')
            generalChannel = discord.utils.get(guild.channels, name=f'debate-{debateID}-general')
            voiceChannel = discord.utils.get(guild.channels, name=f'debate-{debateID}-voice')

            await forChannel.delete()
            await againstChannel.delete()
            await generalChannel.delete()
            await voiceChannel.delete()

            category = discord.utils.get(guild.categories, name=f'Debate {debateID}')
            await category.delete()

            # Delete roles
            forRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : For')
            againstRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : Against')
            modRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : Mod')

            await forRole.delete()
            await againstRole.delete()
            await modRole.delete()

            availableIDs.add(int(debateID))
            await message.channel.send(f'Debate {debateID} closed')

        # Show list of debates
        elif text.startswith('show'):
            # Print details for all open debates
            if len(text) == 4:
                await message.channel.send(f'{len(debateLists)} open debate(s):')
                for openID in debateLists:
                    debateList = debateLists[openID]
                    maxCapacity = debateList['max']
                    nMembers = debateList['nMembers']
                    mod = str(guild.get_member(debateList['modID']))

                    await message.channel.send(f'-> Debate {openID} ({nMembers}/{maxCapacity})\t|\tMod: {mod}')
                return

            # Ensure debate ID is valid
            debateID = await fetchNumber(message, text[4:])
            if debateID is None:
                return

            # Ensure debate <ID> is open
            if debateID not in openIDs:
                await message.channel.send(f'Debate {debateID} is not open')
                return

            # Print debate <ID> details
            debateList = debateLists[debateID]
            memberIDs = debateList['for'] + debateList['against']
            membersStr = list(map(lambda userID : str(guild.get_member(userID)), memberIDs))
            maxCapacity = debateList['max']
            nMembers = debateList['nMembers']
            mod = str(guild.get_member(debateList['modID']))

            await message.channel.send(f'Debate {debateID} ({nMembers}/{maxCapacity}) | Mod: {mod} | Members : {membersStr}')
            return
        
        else:
            return

        await expChannel.send(f'<log>{debateLists}')
        
        ############################################################
        
    except Exception as e:
        await logError(traceback.format_exc())

########################################
client.run(botToken)
