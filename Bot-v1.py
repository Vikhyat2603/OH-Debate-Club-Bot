'''
TODO :
ask if command prefix is needed

-> randomise participants for the purpose of Debate Rooms

-> Another bot to randomise Championship teams who may want to compete with teams
from other groups too - these may be moderated and scored for the purpose of the
wildcard - No House Vote 
'''

import discord
import random

client = discord.Client()
thisBot = client.user

########################################

rules = {'rule 1' : 'sample rule 1 text',
         'rule 2' : 'sample rule 2 text',
         'rule 3' : 'sample rule 3 text',
         'rule 4' : 'sample rule 4 text'}

allRulesList = ['-> ' + ruleNum + ' : ' + rule for ruleNum, rule in rules.items()]
allRules = 'All Rules:\n' + '\n'.join(allRulesList)

debateFormatInfo = '''Hello users,
We are following the -- debate format
You can read about this here : <link>'''

commandPrefix = '!'

creatingList = False
randomRoomUsers = []
maxCapacity = 0
splitDelimiters = ['\\', '/', 'vs', 'v']

removeSpace = lambda s : s.replace(' ','')

########################################

# Respond to messages
@client.event
async def on_message(message):
    
    global randomRoomUsers, creatingList, maxCapacity
    
    text = message.content.strip()
    author = str(message.author)
    message.content = message.content.lower()
    
    if author == thisBot:
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
        return
    
    # State Rules
    if text.startswith('rule'):
        if (text in rules):
            rule = rules[text]
            await message.channel.send('->'+  text + ' : ' + rule)
        elif (text == 'rule all') or (text == 'rules all'):
            await message.channel.send(allRules)
        else:
            await message.channel.send("Rule does not exist")
        return

    ############################################################

    # Start debate with max capacity
    if removeSpace(text).startswith('debatewith'):
        maxStr = removeSpace(text[text.index('h')+1:])
        if maxStr.isdigit():
            maxCapacity = int(maxStr)
            creatingList = True
        else:
            await message.channel.send("'" + maxStr + "'" + " is an invalid number")
        return
    
    # Add user to list
    if text == 'add me':
        if author in randomRoomUsers:
            await message.channel.send(author + " is already in list")
        else:
            if len(randomRoomUsers) == maxCapacity:
                await message.channel.send(f'Max capacity ({maxCapacity}) reached ')
            else:
                randomRoomUsers.append(author)
                await message.channel.send("Added " + author + " to list")
                if len(randomRoomUsers) == maxCapacity:
                    random.shuffle(randomRoomUsers)
                    mid = len(randomRoomUsers)//2
                    
                    sections = [randomRoomUsers[:mid], randomRoomUsers[mid:]]
                    random.shuffle(sections)
                    
                    await message.channel.send("For : " + ', '.join(sections[0]))
                    await message.channel.send("Against : " + ', '.join(sections[1]))
                    
        return
    
    ############################################################
        
# Greet new users on DM
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to the OpenHouse Debate Club Server!')

########################################
  
client.run('NzE1MTc1OTkzNzgyMDQyNjg2.Xs5gyA.zMzZrMXq6dcYTLub2Mo-1ibr9JM')
