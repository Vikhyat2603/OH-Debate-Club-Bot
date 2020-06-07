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

randomRoomUsers = []
splitDelimiters = ['\\', '/', 'vs']

########################################

# Respond to messages
@client.event
async def on_message(message):
    
    global randomRoomUsers
    
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
            
    # Add user to list
    elif text == 'add me':
        if author in randomRoomUsers:
            await message.channel.send(author + " is already in list")
        else:
            randomRoomUsers.append(author)
            await message.channel.send("Added " + author + " to list")

    # Randomise list into 2 sections
    elif text.startswith('split'):

        # Get the names of the 2 sections
        if len(text) > 5:
            groupsStr = text[5:]
            for delimiter in splitDelimiters:
                if delimiter in groupsStr:
                    groups = [g.strip() for g in groupsStr.split(delimiter)]
                    break
            else:
                await message.channel.send("Unknown split character")
                return
        else:
            groups = ['A', 'B'] 
            
        random.shuffle(randomRoomUsers)
        length = len(randomRoomUsers)
        
        section1 = randomRoomUsers[:length//2]
        section2 = randomRoomUsers[length//2:]
        sections = [section1, section2]
        random.shuffle(sections)
        
        await message.channel.send(groups[0] + " : " + ', '.join(sections[0]))
        await message.channel.send(groups[1] + " : " + ', '.join(sections[1]))

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
