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

randomRoomUsers = []
maxCapacity = 0
splitDelimiters = ['\\', '/', 'vs', 'v']

removeSpace = lambda s : s.replace(' ','')

########################################

# Respond to messages
@client.event
async def on_message(message):
    
    global randomRoomUsers, maxCapacity
    
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
        if maxStr.isdigit():
            maxCapacity = int(maxStr)
            randomRoomUsers = []
            await message.channel.send(f'Creating debate with {maxCapacity} members')
        else:
            await message.channel.send(f'\'{maxStr}\' is an invalid number')
    
    # Add user to list
    elif text == 'add me':
        if author in randomRoomUsers:
            await message.channel.send(f'{author} is already in list')
        else:
            if len(randomRoomUsers) == maxCapacity:
                await message.channel.send(f'Max capacity ({maxCapacity}) reached ')
            else:
                randomRoomUsers.append(author)
                await message.channel.send(f'Added {author} to list')
                if len(randomRoomUsers) == maxCapacity:
                    random.shuffle(randomRoomUsers)
                    mid = len(randomRoomUsers)//2
                    
                    sections = [randomRoomUsers[:mid], randomRoomUsers[mid:]]
                    random.shuffle(sections)
                    
                    await message.channel.send('For : '     + ', '.join(sections[0]))
                    await message.channel.send('Against : ' + ', '.join(sections[1]))

    # Print list
    elif text == 'print':
        await message.channel.send("List: " + ', '.join(randomRoomUsers))
        
    # Clear list
    elif text == 'clear':
        randomRoomUsers = []
        await message.channel.send("List cleared")
        
    ############################################################
        
# Greet new users on DM
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to the OpenHouse Debate Club Server!')

########################################
  
client.run('NzE1MTc1OTkzNzgyMDQyNjg2.Xs5gyA.zMzZrMXq6dcYTLub2Mo-1ibr9JM')
