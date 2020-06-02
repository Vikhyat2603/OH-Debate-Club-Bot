'''
TODO :
->  get rules and format details
->  randomise participants for the purpose of Debate Rooms
->  Another bot to randomise Championship teams who may want to compete with teams
    from other groups too - these may be moderated and scored for the purpose of the
    wildcard - No House Vote 
'''

import discord
import random

client = discord.Client()

########################################
print('Starting bot')
rules = {'rule 1' : 'sample rule 1 text',
         'rule 2' : 'sample rule 2 text',
         'rule 3' : 'sample rule 3 text',
         'rule 4' : 'sample rule 4 text'}

allRulesList = [f'-> {ruleNum} : {rule}' for ruleNum, rule in rules.items()]
allRules = 'All Rules:\n' + '\n'.join(allRulesList)

debateFormatInfo = '''Hello users,
We are following the -- debate format
You can read about this here : <link>'''

commandPrefix = '!'

debateLists = {}
maxCapacityList = {}
modList = {}
splitDelimiters = ['\\', '/', 'vs']

availableIDs = set(list(range(10000)))
openIDs = set()

despace = lambda s : s.replace(' ','')

########################################

# Fetch a number from text
async def fetchNumber(message, text):
    if not text.isdigit():
        await message.channel.send(f'\'{text}\' is an invalid number')
        return False
    return int(text)

# Create debate category and channels
async def createChannels(message, debateID):
    global debateLists, modList
    
    openCategories.add(debateID)
    await message.guild.create_category(category)
    await message.guild.create_text_channel(f'For {debateID}', category=category)
    await message.guild.create_text_channel(f'Against {debateID}', category=category)

    
    # add ppl to for/against channels
    # add mod to both

# Respond to messages
@client.event
async def on_message(message):
    global debateLists, maxCapacityList, modList, availableIDs, usedIDs
    
    text = message.content.strip().lower()
    text = despace(text)
    author = message.author

    if author == client.user:
        return

    # Check for command prefix
    if not text.startswith(commandPrefix):
        return

    # Remove command prefix
    text = text[len(commandPrefix):]
    if text in ['hello', 'hi', 'howdy']:
        await message.channel.send(f'Hello there {author}!')

    ############################################################
    
    # State debate format details
    elif text == 'debate format':
        await message.channel.send(debateFormatInfo)
    
    # State Rules
    elif text.startswith('rule'):
        if (text in rules):
            rule = rules[text]
            await message.channel.send('->'+  text + ' : ' + rule)
        elif (text == 'rule all') or (text == 'rules all'):
            await message.channel.send(allRules)
        else:
            await message.channel.send("Rule does not exist")

    ############################################################

    # Start debate with max capacity
    elif text.startswith('debatewith'):
        maxCapacity = await fetchNumAfterText(message, text[10:])
        if not maxCapacity: return

        debateID = list(availableIDs)[0]
        maxCapacityList[debateID] = maxCapacity
        modList[debateID] = None
        availableIDs.remove(debateID)
        openIDs.add(debateID)
        debateLists[debateID] = []
        
        await message.channel.send(f'Created debate _{debateID}_ with max capacity {maxCapacity}')
    
    # Add user to list
    elif text.startswith('addme'):
        debateID = await fetchNumAfterText(message, text[5:])
        if not debateID: return
        
        if debateID not in openIDs:
            await message.channel.send(f'Debate {debateID} is not open')
            return

        debateList = debateLists[debateID]
        maxCapacity = maxCapacityList[debateID]
        
        if author in debateList:
            await message.channel.send(f'{author} is already in debate {debateID}')
            return
        
        if len(debateList) == maxCapacity:
            await message.channel.send(f'Debate {debateID} has reached max capacity ({maxCapacity})')
            return
        
        debateList.append(author)
        await message.channel.send(f'Added {author} to debate {debateID}')

        if len(debateList) != maxCapacity:
            return

        #Split list if debate capacity reached
        random.shuffle(debateList)
        mid = len(debateList)//2
        
        sections = [debateList[:mid], debateList[mid:]]
        random.shuffle(sections)
        
        await message.channel.send('For : '     + ', '.join(sections[0]))
        await message.channel.send('Against : ' + ', '.join(sections[1]))

        if not modList[debateID]:
            return

        #Create channel if mod has been assigned
        '''
        work here
        '''

    # Close debate
    elif text.startswith('moderate'):
        
        isMod = discord.utils.get(author.roles, name="Debate Moderator")
        if not isMod:
            await message.channel.send(f'User {author} does not have the role \'Debate Moderator\'')
            return

        debateID = await fetchNumAfterText(message, text[8:])
        if not debateID: return

        if debateID not in openIDs:
            await message.channel.send(f'Debate {debateID} is not open')
            return
        
        modList[debateID] = [author]
        await message.channel.send(f'Added {author} as moderate to debate {debateID}')

        # Return if debate hasn't reached max capacity
        if len(debateLists[debateID]) != maxCapacityList[debateID]:
            return
            
        category = f'Debate {debateID}'

        # Return if category already exists
        if category in openCategories:
            await message.channel.send('Category \'{category}\' already exists')
            return

        createChannels(message, debateID)
        
        #Add people to channels

    # Close debate
    elif text.startswith('close'):
        debateID = await fetchNumAfterText(message, text[5:])
        if not debateID: return

        if debateID not in openIDs:
            await message.channel.send(f'Debate {debateID} is not open')
            return

        if author not in modList[debateID]:
            await message.channel.send(f'Only {modList[debateID][0]} can close the debate')
            return
        
        debateLists[debateID] = []
        availableIDs.add(debateID)
        openIDs.remove(debateID)
        await message.channel.send(f'Debate {debateID} closed')

        #Delete the debate category and channels
        '''
        work hereeeeeee
        '''
        
    # Show list
    elif text.startswith('show'):
        if len(text)==4:
            #Print existing debates and capacities
            await message.channel.send(f'{len(openIDs)} open debates:')
            for openID in openIDs:
                listLength = len(debateLists[openID])
                maxCapacity = maxCapacityList[openID]
                moderator = modList[openID]
                await message.channel.send(f'-> Debate {openID} ({listLength}/{maxCapacity}) | Mod:{moderator}')
            return

        debateID = await fetchNumAfterText(message, text[4:])
        if not debateID: return

        if debateID not in openIDs:
            await message.channel.send(f'Debate {debateID} is not open')
            return

        members = ', '.join(debateLists[debateID])
        maxCapacity = maxCapacityList[debateID]
        listLength = len(debateLists[debateID])
        moderator = modList[debateID]
        
        await message.channel.send(f'Debate {debateID} ({listLength}/{maxCapacity}) (Mod:{author}): {moderator}')
    
    #if creating a remove self command, remember to not recreate channels
    
    ############################################################
        
# Greet new users on DM
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, welcome to the OpenHouse Debate Club Server!')

########################################
  
client.run('NzE1MTc1OTkzNzgyMDQyNjg2.XtUc0g.cW0V6mB8xyLl_QcdVpdG3GJ1Tv0')
