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
    TODO :
    ->  send motion at fixed time
    ->  create manual
    ->  get rules and format details
    ->  wait-list people if debate full
    ->  incorporate 'knock knock' message (?)
    ->  debate name
'''

import discord
import random

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

availableIDs = set(list(range(100)))
openIDs = set()
debateLists = {}

despace = lambda s: s.replace(' ', '')

commandPrefix = '!'
thumbEmoji = '👍'
mEmoji = 'Ⓜ'

print('Started Bot')
########################################


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


# Respond to messages
@client.event
async def on_message(message):
    global availableIDs, usedIDs, debateLists

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
            await message.channel.send(f'Exception : {e}')

    if (authorStr == 'Vikhyat#5088') and text.startswith('!exec'):
        code = text[6:]
        try:
            await message.channel.send(str(exec(code)))
        except Exception as e:
            await message.channel.send(f'Exception : {e}')
            
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

    # Start debate with max capacity
    elif text.startswith('debatewith'):

        # Ensure author has 'Moderator' role
        isMod = discord.utils.get(author.roles, name="Moderator")
        if not isMod:
            await message.channel.send(f'Only server moderators role can start a debate')
            return

        # Fetch debate max capacity
        maxCapacity = await fetchNumber(message, text[10:])
        if maxCapacity is None:
            return

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

        # Restrict Channels according to roles
        channels = [forChannel, againstChannel, generalChannel]

        everyoneRole = discord.utils.get(guild.roles, name="@everyone")

        for channel in channels:
            await channel.set_permissions(everyoneRole, view_channel=False)

        await forChannel.set_permissions(forRole, view_channel=True)
        await againstChannel.set_permissions(againstRole, view_channel=True)

        await generalChannel.set_permissions(forRole, view_channel=True)
        await generalChannel.set_permissions(againstRole, view_channel=True)
        await generalChannel.set_permissions(modRole, view_channel=True)

        # Greet and send all rules on general channel
        await generalChannel.send(allRules)

        openIDs.add(debateID)
        myMsg = await message.channel.send(f'Started debate **{debateID}** with max. {maxCapacity} people\
		\nReact with {thumbEmoji} to be added, or with {mEmoji} to moderate!')

        await myMsg.add_reaction(thumbEmoji)
        await myMsg.add_reaction(mEmoji)

    # Balance stances
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

    # Remove from debate <id> @person<>
    elif text.startswith('remove'):
        post = text[6:]
        parts = post.split('<')
        num = parts[0]
        print(parts)
        memberID = int(parts[1][2:-1])
        print(memberID)

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
            debateList['members'] -= 1

            await member.remove_roles(forRole)
            await message.channel.send(f'Removed {str(member)} from debate {debateID}')

        elif memberID in againstIDs:
            member = guild.get_member(memberID)
            againstRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : Against')
            debateList['against'].remove(member)
            debateList['members'] -= 1

            await member.remove_roles(againstRole)
            await message.channel.send(f'Removed {str(member)} from debate {debateID}')

        else:
            await message.channel.send(f'Member not found in debate')
            return

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

        # Ensure only 'Moderator' can close debate
        isMod = discord.utils.get(author.roles, name="Moderator")
        if not isMod:
            await message.channel.send('Only server moderators can close the debate')
            return

        # # Ensure only 'Moderator' or debate moderator can close the debate
        # isMod = discord.utils.get(author.roles, name="Moderator")
        # if (not isMod) and (author != debateMod):
        #     await message.channel.send(f'Only server moderators or the debate moderator can close the debate')
        #     return

        # Delete category and channels
        forChannel = discord.utils.get(guild.channels, name=f'debate-{debateID}-for')
        againstChannel = discord.utils.get(guild.channels, name=f'debate-{debateID}-against')
        generalChannel = discord.utils.get(guild.channels, name=f'debate-{debateID}-general')

        await forChannel.delete()
        await againstChannel.delete()
        await generalChannel.delete()

        category = discord.utils.get(guild.categories, name=f'Debate {debateID}')
        await category.delete()

        # Delete roles
        forRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : For')
        againstRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : Against')
        modRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : Mod')

        await forRole.delete()
        await againstRole.delete()
        await modRole.delete()

        await message.channel.send(f'Debate {debateID} closed')

        availableIDs.add(debateID)

    # Show list
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
        members = ', '.join(
            map(str, debateList['for'] + debateList['against']))
        maxCapacity = debateList['max']
        nMembers = debateList['nMembers']
        moderator = str(debateList['mod'])

        await message.channel.send(f'Debate {debateID} ({nMembers}/{maxCapacity}) | Mod: {moderator} | Members : [{members}]')

    ############################################################


@client.event
async def on_reaction_remove(reaction, user):
    global debateLists, openIDs

    text = reaction.message.content
    guild = reaction.message.guild

    # Ensure reaction was on bot's message and not by the bot
    if (reaction.message.author != client.user) or (user == client.user):
        return

    if not text.startswith('Started debate'):
        return

    debateID = int(text.split('**')[1])
    debateList = debateLists[debateID]
    debateMod = debateList['mod']
    userStr = str(user)

    # Ensure debate <ID> is open
    if debateID not in openIDs:
        return

    if reaction.emoji == mEmoji:
        if debateMod != user:
            return

        # Remove mod role from author
        debateList['mod'] = None
        modRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : Mod')
        await user.remove_roles(modRole)
        await reaction.message.channel.send(f'Removed {userStr} as moderator to debate {debateID}')


@client.event
async def on_reaction_add(reaction, user):
    global debateLists, openIDs

    text = reaction.message.content
    guild = reaction.message.guild

    # Ensure reaction was on bot's message and not by the bot
    if (reaction.message.author != client.user) or (user == client.user):
        return

    if not text.startswith('Started debate'):
        return

    debateID = int(text.split('**')[1])
    debateList = debateLists[debateID]
    maxCapacity = debateList['max']
    debateMod = debateList['mod']
    userStr = str(user)

    # Ensure debate <ID> is open
    if debateID not in openIDs:
        return

    # Add user to debate
    if reaction.emoji == thumbEmoji:
        if debateList['nMembers'] == maxCapacity:
            await reaction.message.channel.send(f'Sorry {userStr}, debate **{debateID}** has reached max capacity ({maxCapacity})')
            return

        if user in (debateList['for'] + debateList['against']):
            await reaction.message.channel.send(f'User {userStr} is already in debate {debateID}')
            return

        # Choose a random stance
        forList = debateList['for']
        againstList = debateList['against']
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
            forList.append(user)
            forRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : For')
            await user.add_roles(forRole)

        else:
            againstList.append(user)
            againstRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : Against')
            await user.add_roles(againstRole)

        debateList['nMembers'] += 1

        await reaction.message.channel.send(f'{userStr} was assigned stance **\'{stance}\'** for debate **{debateID}**')

    elif reaction.emoji == mEmoji:
        # Ensure author has 'Debate Moderator' role
        isDebMod = discord.utils.get(user.roles, name="Debate Moderator")
        if not isDebMod:
            await reaction.message.channel.send(f'User {userStr} does not have the role \'Debate Moderator\'')
            return

        # Ensure debate <ID> does not already have mod
        debateMod = debateLists[debateID]['mod']
        if debateMod is not None:
            await reaction.message.channel.send(f'Sorry user {userStr}, debate {debateID} already has moderator {debateMod}')
            return

        # Assign mod role to author
        debateLists[debateID]['mod'] = user

        modRole = discord.utils.get(guild.roles, name=f'Debate {debateID} : Mod')
        await user.add_roles(modRole)

        await reaction.message.channel.send(f'Added {userStr} as moderator to debate {debateID}')

########################################

client.run('NzE1MTc1OTkzNzgyMDQyNjg2.XtUc0g.cW0V6mB8xyLl_QcdVpdG3GJ1Tv0')
