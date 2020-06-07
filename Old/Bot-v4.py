'''
TODO :
->  DONE 'Moderator' role can close any debate
->  DONE only admins can start debates
->  DONE show <id> also lists members
->  DONE balance <id>
->  DONE moderate by reacting with M?
->  DONE opt-out by de-selecting
->  DONE !query (anonymous?)
->  DONE dont let ppl opt-out
->  DONE let debate mods and mods remove person <> from debate <>

->  send motion
->  create manual
->  get rules and format details

-> wait-list option
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

debateFormatInfo = '''Hello users,
We are following the -- debate format
You can read about this here : <link>'''

commandPrefix = '!'

debateLists = {}
myGuild = client.get_guild(714853767841054721)

availableIDs = set(list(range(10000)))
openIDs = set()

despace = lambda s: s.replace(' ', '')

thumbEmoji = '👍'
mEmoji = 'Ⓜ'

print('Started Bot')
########################################


# Fetch a number from text
async def fetchNumber(message, text):
    if not text.isdigit():
        await message.channel.send(f'\'{text}\' is an invalid number')
        return None
    return int(text)


@client.event
async def on_reaction_remove(reaction, user):
    global debateLists, maxCapacityList, openIDs

    text = reaction.message.content
    guild = reaction.message.guild

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

    if debateList['busy']:
        await reaction.message.channel.send(f'Sorry {userStr}, I\'m currently working on managing this debate')
        return

   # if reaction.emoji == thumbEmoji:
   #     # Remove person from debateLists[stance] and remove roles

   #     forList = debateList['for']
   #     againstList = debateList['against']

   #     if user in forList:
   #         forRoleName = f'Debate {debateID} : For'
   #         forRole = discord.utils.get(guild.roles, name=forRoleName)
   #         forList.remove(user)
   #         await user.remove_roles(forRole)

   #     elif user in againstList:
   #         againstRoleName = f'Debate {debateID} : Against'
   #         againstRole = discord.utils.get(guild.roles, name=againstRoleName)
   #         againstList.remove(user)
   #         await user.remove_roles(againstRole)
   #     else:
   #         return

   #     debateList['nMembers'] -= 1

   # await reaction.message.channel.send(f'User {userStr} removed from debate
   # {debateID}')

    if reaction.emoji == mEmoji:

        if debateMod != user:
            return

        # Remove mod role from author
        debateList['mod'] = None

        modRoleName = f'Debate {debateID} : Mod'
        modRole = discord.utils.get(guild.roles, name=modRoleName)
        await user.remove_roles(modRole)

        await reaction.message.channel.send(f'Removed {userStr} as moderator to debate {debateID}')


# Add user on message reaction
@client.event
async def on_reaction_add(reaction, user):
    global debateLists, maxCapacityList, openIDs

    text = reaction.message.content
    guild = reaction.message.guild

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

    if debateList['busy']:
        await reaction.message.channel.send(f'Sorry {userStr}, I\'m currently working on managing this debate')
        return

    # Add user to debate
    if reaction.emoji == thumbEmoji:
        if debateList['nMembers'] == maxCapacity:
            await reaction.message.channel.send(f'Sorry {userStr}, debate **{debateID}** has reached max capacity ({maxCapacity})')
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
            forRoleName = f'Debate {debateID} : For'
            forRole = discord.utils.get(guild.roles, name=forRoleName)
            await user.add_roles(forRole)

        else:
            againstList.append(user)
            againstRoleName = f'Debate {debateID} : Against'
            againstRole = discord.utils.get(guild.roles, name=againstRoleName)
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

        modRoleName = f'Debate {debateID} : Mod'
        modRole = discord.utils.get(guild.roles, name=modRoleName)
        await user.add_roles(modRole)

        await reaction.message.channel.send(f'Added {userStr} as moderator to debate {debateID}')


# Respond to messages
@client.event
async def on_message(message):
    global debateLists, maxCapacityList, modList, availableIDs, usedIDs

    text = message.content
    author = message.author
    authorStr = str(author)
    guild = message.guild

    if (authorStr == 'Vikhyat#5088') and text.startswith('!debug'):
        code = text[6:]
        try:
            await message.channel.send(eval(code))
        except Exception as e:
            await message.channel.send(e)

    if text.startswith('!query'):
        query = text[6:]
        myGuild = client.get_guild(714853767841054721)

        queryMessage = '-' * 80 + f'\nUser : {authorStr}\nQuery : {query}'
        queryChannel = discord.utils.get(myGuild.channels, name=f'queries')
        await queryChannel.send(queryMessage)
        await message.channel.send('Sent:\n' + queryMessage)

        return

    text = despace(text.lower())

    if author == client.user:
        if text.startswith('starteddebate'):
            await message.add_reaction(thumbEmoji)
            await message.add_reaction(mEmoji)
        return

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
            await message.channel.send('->' + text + ' : ' + rule)
        elif (text == 'ruleall') or (text == 'rulesall') or(text == 'rules'):
            await message.channel.send(allRules)
        else:
            await message.channel.send("Rule does not exist")

    ############################################################

    # Start debate with max capacity
    elif text.startswith('debatewith'):

        # Ensure author has 'Moderator' role
        isMod = discord.utils.get(author.roles, name="Moderator")
        if not isMod:
            await message.channel.send(f'User {author} does not have the role \'Moderator\'')
            return

        # Fetch debate max capacity
        maxCapacity = await fetchNumber(message, text[10:])
        if maxCapacity is None:
            return

        # Initialise debate details
        debateID = list(availableIDs)[0]
        availableIDs.remove(debateID)
        openIDs.add(debateID)
        debateLists[debateID] = {'nMembers': 0,
                                 'for': [],
                                 'against': [],
                                 'mod': None,
                                 'max': maxCapacity,
                                 'busy':True}

        # Create roles : for, against and mod
        forRoleName = f'Debate {debateID} : For'
        againstRoleName = f'Debate {debateID} : Against'
        modRoleName = f'Debate {debateID} : Mod'

        await guild.create_role(name=forRoleName)
        await guild.create_role(name=againstRoleName)
        await guild.create_role(name=modRoleName)

        # Create categories and channels
        categoryName = f'Debate {debateID}'
        await guild.create_category(categoryName)

        category = discord.utils.get(guild.categories, name=categoryName)
        prefixes = ['general', 'for', 'against']
        for prefix in prefixes:
            await guild.create_text_channel(f'debate-{debateID}-{prefix}', category=category)

        # Restrict Channels according to roles
        forChannel = discord.utils.get(guild.channels, name=f'debate-{debateID}-for')
        againstChannel = discord.utils.get(guild.channels, name=f'debate-{debateID}-against')
        generalChannel = discord.utils.get(guild.channels, name=f'debate-{debateID}-general')

        channels = [forChannel, againstChannel, generalChannel]

        everyoneRole = discord.utils.get(guild.roles, name="@everyone")
        forRole = discord.utils.get(guild.roles, name=forRoleName)
        againstRole = discord.utils.get(guild.roles, name=againstRoleName)
        modRole = discord.utils.get(guild.roles, name=modRoleName)

        for channel in channels:
            await channel.set_permissions(everyoneRole, view_channel=False)
            await channel.set_permissions(modRole, view_channel=True)

        await forChannel.set_permissions(forRole, view_channel=True)
        await generalChannel.set_permissions(forRole, view_channel=True)

        await againstChannel.set_permissions(againstRole, view_channel=True)
        await generalChannel.set_permissions(againstRole, view_channel=True)

        # Greet and send all rules on general channel
        await generalChannel.send(allRules)

        debateLists[debateID]['busy'] = False
        await message.channel.send(f'Started debate **{debateID}** with max. {maxCapacity} people\
		\nReact with {thumbEmoji} to be added, or with {mEmoji} to moderate!')

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

        if debateList['busy']:
            await reaction.message.channel.send(f'Sorry {authorStr}, I\'m currently working on managing this debate')
            return

        # Ensure only 'Moderator' # or debate's moderator can balance debate
        isMod = discord.utils.get(author.roles, name="Moderator")
        if not isMod:
            await message.channel.send(f'User {author} does not have the \'Moderator\' role')
            # Ensure debate <ID> has a mod
            if debateMod is None:
                await message.channel.send(f'Only the moderator for debate {debateID} can balance the stances')

                return

            # Ensure author is mod for debate <ID>
            if author != debateMod:
                await message.channel.send(f'Only {debateMod} can balance the stances')
                return
            return

        # Split members into 2 stances
        members = debateList['for'] + debateList['against']
        random.shuffle(members)
        mid = len(members) // 2
        sections = [members[:mid], members[mid:]]
        random.shuffle(sections)

        # Remove old stance roles
        forRoleName = f'Debate {debateID} : For'
        againstRoleName = f'Debate {debateID} : Against'

        forRole = discord.utils.get(guild.roles, name=forRoleName)
        againstRole = discord.utils.get(guild.roles, name=againstRoleName)

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

    # Remove from debate <id>, person <>
    elif text.startswith('remove'):
        post = text[6:]
        parts = post.split('<')
        num = parts[0]
        memberID = parts[1][1:-1]

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

        if debateList['busy']:
            await reaction.message.channel.send(f'Sorry {authorStr}, I\'m currently working on managing this debate')
            return

        # Ensure only 'Moderator' or debate moderator can close debate
        isMod = discord.utils.get(author.roles, name="Moderator")
        if (not isMod) and (author != debateMod):
            await message.channel.send(f'Only the debate moderator can remove members')
            return

        forIDs = [m.id for m in debateList['for']]
        againstIDs = [m.id for m in debateList['against']]
        print(forIDs, againstIDs, memberID)

        if memberID in forIDs:
            member = guild.get_member(memberID)
            forRoleName = f'Debate {debateID} : For'
            forRole = discord.utils.get(guild.roles, name=forRoleName)
            forList.remove(member)
            await member.remove_roles(forRole)

        elif memberID in againstIDs:
            member = guild.get_member(memberID)
            againstRoleName = f'Debate {debateID} : Against'
            againstRole = discord.utils.get(guild.roles, name=againstRoleName)
            againstList.remove(member)
            await member.remove_roles(againstRole)

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
        debateMod = debateList['mod']

        if debateList['busy']:
            await reaction.message.channel.send(f'Sorry {authorStr}, I\'m currently working on managing this debate')
            return

        debateList['busy'] = True
        
        # Ensure only 'Moderator' or debate's moderator can close debate
        isMod = discord.utils.get(author.roles, name="Moderator")
        if not isMod:
            await message.channel.send(f'Only members with the \'Moderator\' role can close the debate')
            return

            # Ensure author is mod for debate <ID>
            # if author != debateMod:
            #     await message.channel.send(f'Only the moderator for this debate can close it')
            #     return

        # Delete category and channels
        forChannel = discord.utils.get(guild.channels, name=f'debate-{debateID}-for')
        againstChannel = discord.utils.get(guild.channels, name=f'debate-{debateID}-against')
        generalChannel = discord.utils.get(guild.channels, name=f'debate-{debateID}-general')

        await forChannel.delete()
        await againstChannel.delete()
        await generalChannel.delete()

        categoryName = f'Debate {debateID}'
        category = discord.utils.get(guild.categories, name=categoryName)
        await category.delete()

        # Delete roles
        forRoleName = f'Debate {debateID} : For'
        againstRoleName = f'Debate {debateID} : Against'
        modRoleName = f'Debate {debateID} : Mod'

        forRole = discord.utils.get(guild.roles, name=forRoleName)
        againstRole = discord.utils.get(guild.roles, name=againstRoleName)
        modRole = discord.utils.get(guild.roles, name=modRoleName)

        await forRole.delete()
        await againstRole.delete()
        await modRole.delete()

        await message.channel.send(f'Debate {debateID} closed')

        availableIDs.add(debateID)
        openIDs.remove(debateID)
        debateList['busy'] = False

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
        members = ', '.join(map(str, debateList['for'] + debateList['against']))
        maxCapacity = debateList['max']
        nMembers = debateList['nMembers']
        moderator = str(debateList['mod'])

        await message.channel.send(f'Debate {debateID} ({nMembers}/{maxCapacity}) | Mod: {moderator} | Members : [{members}]')

    ############################################################


# Greet new users on DM
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, welcome to the OpenHouse Debate Club Server!')
    await member.dm_channel.send(allRules)

########################################

client.run('NzE1MTc1OTkzNzgyMDQyNjg2.XtUc0g.cW0V6mB8xyLl_QcdVpdG3GJ1Tv0')
