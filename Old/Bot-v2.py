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
splitDelimiters = ['\\', '/', 'vs']

availableIDs = set(list(range(10000)))
openIDs = set()

removeSpace = lambda s : s.replace(' ','')

########################################

# Respond to messages
@client.event
async def on_message(message):
    
    global debateLists, maxCapacityList, availableIDs
    
    text = message.content.strip().lower()
    author = str(message.author)
    
    if author == client.user:
        return

    # Check for command prefix
    if not text.startswith(commandPrefix):
        return

    # Remove command prefix
    text = text[len(commandPrefix):]

    ############################################################
    
    # State debate format details
    if text == 'debate format':
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
    elif removeSpace(text).startswith('debatewith'):
        maxStr = removeSpace(text[text.index('h')+1:])
        if not maxStr.isdigit():
            await message.channel.send(f'\'{maxStr}\' is an invalid number')
            return
        
        maxCapacity = int(maxStr)

        debateID = list(availableIDs)[0]
        maxCapacityList[debateID] = maxCapacity
        availableIDs.remove(debateID)
        openIDs.add(debateID)
        debateLists[debateID] = []
        
        await message.channel.send(f'Created debate _{debateID}_ with max capacity {maxCapacity}')
    
    # Add user to list
    elif removeSpace(text).startswith('addme'):
        idStr = removeSpace(text[text.index('e')+1:])
        if not idStr.isdigit():
            await message.channel.send(f'\'{idStr}\' is an invalid debate ID')
            return

        debateID = int(idStr)

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
        
        if len(debateList) == maxCapacity:
            random.shuffle(debateList)
            mid = len(debateList)//2
            
            sections = [debateList[:mid], debateList[mid:]]
            random.shuffle(sections)
            
            await message.channel.send('For : '     + ', '.join(sections[0]))
            await message.channel.send('Against : ' + ', '.join(sections[1]))

    # Show list
    elif removeSpace(text).startswith('show'):
        if len(text)==4:
            #Print existing debates and capacities
            await message.channel.send(f'{len(openIDs)} open debates:')
            for openID in openIDs:
                listLength = len(debateLists[openID])
                maxCapacity = maxCapacityList[openID]
                await message.channel.send(f'-> Debate {openID} ({listLength}/{maxCapacity})')
            return
        
        idStr = removeSpace(text[text.index('t')+1:])
        if not idStr.isdigit():
            await message.channel.send(f'\'{idStr}\' is an invalid debate ID')
            return

        debateID = int(idStr)

        if debateID not in openIDs:
            await message.channel.send(f'Debate {debateID} is not open')
            return

        members = ', '.join(debateLists[debateID])
        maxCapacity = maxCapacityList[debateID]
        listLength = len(debateLists[debateID])
        
        await message.channel.send(f'Debate {debateID} ({listLength}/{maxCapacity}) : {members}')
        
    # Close debate
    elif removeSpace(text).startswith('close'):
        
        idStr = removeSpace(text[text.index('e')+1:])
        if not idStr.isdigit():
            await message.channel.send(f'\'{idStr}\' is an invalid debate ID')
            return

        debateID = int(idStr)

        if debateID not in openIDs:
            await message.channel.send(f'Debate {debateID} is not open')
            return
        
        debateLists[debateID] = []
        availableIDs.add(debateID)
        openIDs.remove(debateID)
        await message.channel.send(f'Debate {debateID} closed')

    ############################################################
        
# Greet new users on DM
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, welcome to the OpenHouse Debate Club Server!')

########################################
  
client.run('NzE1MTc1OTkzNzgyMDQyNjg2.Xs5gyA.zMzZrMXq6dcYTLub2Mo-1ibr9JM')
