'''
Changes (since last meeting):
    DONE :
    ->  DONE 'Moderator' role can close any debate
    ->  DONE only admins can start debates
    ->  DONE show <id> also lists members
    ->  DONE balance <id>
    ->  DONE moderate by reacting with M?
    ->  DONE opt-out by de-selecting
    ->  DONE !query (anonymous?)
    ->  DONE dont let ppl opt-out
    ->  DONE let debate mods and mods remove person <> from debate <>

    --- 17-Jun-20
    ->  Wrap code in try-except
    ->  add voice channel to debate category
    ->  incorporated 'knock knock' message into bot
    ->  Change debatewith command to allow random text after max. cap.
    ->  Participants join by "!add me <ID>"
    ->  Moderators join by "!moderator <ID>"
    ->  Moderators can't be participants

    TODO :
    ->  send motion at fixed time
    ->  create manual
    ->  get rules and format details

    --- 17-Jun-20
    ->  Discussion room
    ->  wait-list people if debate full
'''

import discord
import random
from time import sleep
import asyncio

client = discord.Client()

########################################
rules = {'rule1': 'sample rule 1 text',
         'rule2': 'sample rule 2 text',
         'rule3': 'sample rule 3 text',
         'rule4': 'sample rule 4 text'}

allRulesList = [f'-> {ruleNum} : {rule}' for ruleNum, rule in rules.items()]
allRules = 'All Rules:\n' + '\n'.join(allRulesList)

welcomeMessage = '''Thank you for joining Openhouse Debate Club on Discord, we are so excited to have you on board!
Don’t worry if the new system seems challenging, we are here to help. All the channels here are like different group chats where you can discuss anything you want (channel=chat). Our announcements page will show you the debates you can sign up for. On that debate text, please select the ‘👍’ (thumbs-up) emoji. You will immediately be placed into your team. Introduce yourself to your teammates and get ready to battle it out in your debate! Motions and links for your debate will be sent to you on the channel itself.
Please feel free to message us if you are facing any difficulties. Until then, choose to be better :)'''

debateFormatInfo = '''Hello users,
We are following the -- debate format
You can read about this here : <link>'''

availableIDs = set(list(range(1000)))
openIDs = set()
debateLists = {}

despace = lambda s: s.replace(' ', '')

commandPrefix = '!'
thumbEmoji = '👍'
mEmoji = 'Ⓜ'

print('Started Bot')
########################################

async def logError(myText):
    ohGuild = client.get_guild(714853767841054721)
    expChannel = discord.utils.get(ohGuild.channels, name=f'experiments')
    await expChannel.send('Log: ' + str(myText))

# Greet new users on DM
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, welcome to the **Openhouse Debate Club** Server!')
    await member.dm_channel.send(welcomeMessage)


# Fetch a number from text
async def fetchNumber(message, text):
    if text.isdigit():
        return int(text)
    await message.channel.send(f'\'{text}\' is an invalid number')


# Sends and deletes a message every 29 minutes to keep bot awake
@client.event
async def on_ready():
    ohGuild = client.get_guild(714853767841054721)
    expChannel = discord.utils.get(ohGuild.channels, name='experiments')
    await expChannel.send('Bot Online.')
    while True:    
        myMsg = await expChannel.send('.')
        await myMsg.delete()
        await asyncio.sleep(1750)

# Respond to messages
@client.event
async def on_message(message):
    try:
        global availableIDs, usedIDs, debateLists, rules

        text = message.content
        author = message.author
        authorStr = str(author)
        guild = message.guild

        # Let Vikhyat debug code
        if (authorStr == 'Vikhyat#5088') and text.startswith('!debug'):
            code = text[6:]
            try:
                await message.channel.send(str(eval(code)))
            except Exception as e:
                await message.channel.send(f'{type(e).__name__} :\n{e}')

        if (authorStr == 'Vikhyat#5088') and text.startswith('!exec'):
            code = text[6:]
            try:
                await message.channel.send(str(exec(code)))
            except Exception as e:
                await message.channel.send(f'{type(e).__name__} :\n{e}')

        # Pass queries to the queries channel
        if text.startswith('!query'):
            ohGuild = client.get_guild(714853767841054721)

            query = text[6:]
            queryMessage = ('-' * 80) + f'\nUser : {authorStr}\nQuery : {query}'
            queryChannel = discord.utils.get(ohGuild.channels, name='queries')
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

        ############################################################

        # State debate format details
        elif text == 'debateformat':
            await message.channel.send(debateFormatInfo)

        # State Rules
        elif text.startswith('rule'):
            if (text in rules):
                rule = rules[text]
                await message.channel.send(f'->{text}:{rule}')
            elif text in ['rule', 'rules', 'ruleall', 'rulesall']:
                allRulesList = [f'-> {ruleNum} : {rule}' for ruleNum, rule in rules.items()]
                allRules = 'All Rules:\n' + '\n'.join(allRulesList)
                await message.channel.send(allRules)
            else:
                await message.channel.send("Rule does not exist")

        ############################################################

        # Start debate with fixed max capacity
        elif text.startswith('debatewith'):

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
            debateID = min(availableIDs)
            availableIDs.remove(debateID)
            debateLists[debateID] = {'nMembers': 0,
                                     'for': [],
                                     'against': [],
                                     'mod': None,
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
            channels = [forChannel, againstChannel,
                        generalChannel, voiceChannel]

            everyoneRole = discord.utils.get(guild.roles, name="@everyone")

            for channel in channels:
                await channel.set_permissions(everyoneRole, view_channel=False)

            await forChannel.set_permissions(forRole, view_channel=True)
            await againstChannel.set_permissions(againstRole, view_channel=True)

            commonChannels = [generalChannel, voiceChannel]
            for comChannel in commonChannels:
                await comChannel.set_permissions(forRole, view_channel=True)
                await comChannel.set_permissions(againstRole, view_channel=True)
                await comChannel.set_permissions(modRole, view_channel=True)

            openIDs.add(debateID)
            myMsg = await message.channel.send(f'Started debate **{debateID}** with max. {maxCapacity} people\
                    \nWrite *!add me {debateID}*  to be added, or *!moderate {debateID}*  to moderate!')

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
            debateMod = debateList['mod']
            maxCapacity = debateList['max']
            forList = debateList['for']
            againstList = debateList['against']

            if debateList['nMembers'] == maxCapacity:
                await message.channel.send(f'Sorry {authorStr}, debate **{debateID}** has reached max capacity ({maxCapacity})')
                return

            if author in (forList + againstList):
                await message.channel.send(f'User {authorStr} is already in debate {debateID}')
                return

            if author == debateMod:
                await message.channel.send(f'User {authorStr} is the moderator for debate {debateID}, cannot be a participant too')
                return

            # Choose a random stance
            half = maxCapacity // 2
            stance = ''
            randomStance = 'Against' if random.randint(0, 1) else 'For'

            if maxCapacity % 2 == 0:
                if len(forList) == half:
                    stance = 'Against'
                elif len(againstList) == half:
                    stance = 'For'
                else:
                    stance = randomStance
            else:
                if len(forList) == half:
                    if len(againstList) == half:
                        stance = randomStance
                    else:
                        stance = 'Against'
                elif len(againstList) == half:
                    stance = 'For'
                else:
                    stance = randomStance

            # Assign role and stance
            if stance == 'For':
                forList.append(author)
                forRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : For')
                await author.add_roles(forRole)
            else:
                againstList.append(author)
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
            debateMod = debateList['mod']
            debateMembers = debateList['for'] + debateList['against']

            # ensure author isnt participants
            if author in debateMembers:
                await message.channel.send(f'User {authorStr} is a participant in debate {debateID}, cannot be a moderator too')
                return

            # Ensure author has 'Debate Moderator' role
            isDebMod = discord.utils.get(author.roles, name="Debate Moderator")
            if not isDebMod:
                await message.channel.send(f'User {authorStr} does not have the role \'Debate Moderator\'')
                return

            # Ensure debate <ID> does not already have mod
            if debateMod is not None:
                await message.channel.send(f'Sorry user {authorStr}, debate {debateID} already has moderator {debateMod}')
                return

            # Assign mod role to author
            debateList['mod'] = author

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
            debateMod = debateList['mod']

            # Ensure only 'Moderator' or debate's moderator can balance debate
            isMod = discord.utils.get(author.roles, name="Moderator")
            if (not isMod) and (author != debateMod):
                await message.channel.send(f'Only server moderators or the debate moderator can balance the stances')
                return

            # Split members into 2 stances
            members = debateList['for'] + debateList['against']
            random.shuffle(members)
            mid = len(members) // 2
            sections = [members[:mid], members[mid:]]
            random.shuffle(sections)

            # Remove old stance roles
            forRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : For')
            againstRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : Against')

            for user in debateList['for']:
                await user.remove_roles(forRole)

            for user in debateList['against']:
                await user.remove_roles(againstRole)

            # Assign new stance roles
            debateList['for'] = sections[0]
            debateList['against'] = sections[1]

            for user in debateList['for']:
                await user.add_roles(forRole)
                await message.channel.send(f'{str(user)} was assigned stance **\'For\'** for debate **{debateID}**')

            for user in debateList['against']:
                await user.add_roles(againstRole)
                await message.channel.send(f'{str(user)} was assigned stance **\'Against\'** for debate **{debateID}**')

            await message.channel.send(f'Debate {debateID} stances balanced')

            membersStr = ', '.join(list(map(str, members)))
            maxCapacity = debateList['max']
            nMembers = debateList['nMembers']
            moderator = debateList['mod']

            await message.channel.send(f'Debate {debateID} ({nMembers}/{maxCapacity}) | Mod: {moderator} | Members : [{membersStr}]')

        # Remove participant/moderator from debate
        elif text.startswith('remove'):
            post = text[6:]
            parts = post.split('<')
            num = parts[0]
            memberID = int(parts[1][2:-1])

            if num.isdigit():
                debateID = int(num)
            else:
                await message.channel.send(f'\'{num}\' is an invalid number')
                return

            if debateID not in openIDs:
                await message.channel.send(f'Debate {debateID} is not open')
                return

            debateList = debateLists[debateID]
            debateMod = debateList['mod']

            # Ensure only 'Moderator' or debate moderator can remove members
            isMod = discord.utils.get(author.roles, name="Moderator")
            if (not isMod) and (author != debateMod):
                await message.channel.send(f'Only server moderators or the debate moderator can remove members')
                return

            forIDs = [m.id for m in debateList['for']]
            againstIDs = [m.id for m in debateList['against']]

            if memberID in forIDs:
                member = guild.get_member(memberID)
                forRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : For')
                debateList['for'].remove(member)
                debateList['nMembers'] -= 1

                await member.remove_roles(forRole)
                await message.channel.send(f'Removed {str(member)} from debate {debateID}')

            elif memberID in againstIDs:
                member = guild.get_member(memberID)
                againstRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : Against')
                debateList['against'].remove(member)
                debateList['nMembers'] -= 1

                await member.remove_roles(againstRole)
                await message.channel.send(f'Removed {str(member)} from debate {debateID}')

            # Remove mod role from author
            elif (debateMod is not None) and (memberID == debateMod.id):
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
            openIDs.remove(debateID)

            debateMod = debateList['mod']

            # Ensure only 'Moderator' or debate moderator can close the debate
            isMod = discord.utils.get(author.roles, name="Moderator")
            if (not isMod) and (author != debateMod):
                await message.channel.send(f'Only server moderators or the debate moderator can close the debate')
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

            availableIDs.add(debateID)
            await message.channel.send(f'Debate {debateID} closed')

        # Show list of debates
        elif text.startswith('show'):
            # Print details for all open debates
            if len(text) == 4:
                await message.channel.send(f'{len(openIDs)} open debate(s):')
                for openID in openIDs:
                    debateList = debateLists[openID]
                    maxCapacity = debateList['max']
                    nMembers = debateList['nMembers']
                    moderator = str(debateList['mod'])

                    await message.channel.send(f'Debate {openID} ({nMembers}/{maxCapacity})\t|\tMod: {moderator}')
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
            members = ', '.join(map(str, debateList['for'] + debateList['against']))
            maxCapacity = debateList['max']
            nMembers = debateList['nMembers']
            moderator = str(debateList['mod'])

            await message.channel.send(f'Debate {debateID} ({nMembers}/{maxCapacity}) | Mod: {moderator} | Members : [{members}]')

        ############################################################
    except Exception as e:
        await logError(f'**{type(e).__name__}** :\n{e}')

########################################

client.run('NzE1MTc1OTkzNzgyMDQyNjg2.XtUc0g.cW0V6mB8xyLl_QcdVpdG3GJ1Tv0')
