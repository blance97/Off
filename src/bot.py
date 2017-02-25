import os
import time
import json
import random
import math
import markovify
from slackclient import SlackClient
from firebase import firebase

firebase = firebase.FirebaseApplication('https://slackbotadventures.firebaseio.com/', None)
with open("output.txt") as f:
    text = f.read()

text_model = markovify.Text(text)
# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")
BOT_ID = 'U4AA1UYN7'

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
slack_client = SlackClient('xoxb-146341984755-RGiblWd6w7vnPLWpvSKXB5kK')


def handle_command(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    if command.startswith("newchar"):
        response = new_user(command.split(" ")[1],user)
    elif command.startswith("tradelist"):
        if firebase.get('/Characters/'+ user + '/Meta/trader', None) == "general manager":
            with open('config/items.json') as itemf:
                item = json.load(itemf)
            pot = item.get("Potions")
            response = "/*******************TRADE LIST*********************"
            for pots in pot:
                response += "\n*" +pots.get("name") + "*-------------"+str(pots.get("saleCost"))
            response += "\nYou have $$$" + str(firebase.get('/Characters/'+user+'/Meta/money', None)) + " *cash DOLLA*"
        else:
            response = firebase.get('/Characters/'+ user + 'Meta/trader', None)
    elif command.startswith("buy"):
        stuff = command.split(' ')
        if firebase.get('/Characters/'+ user + '/Meta/trader', None) == "general manager":
            with open('config/items.json') as itemf:
                item = json.load(itemf)
            pot = item.get("Potions")
            response = "/*******************TRADE LIST*********************"
            count = 0
            parsed = ""
            for stuffs in stuff:
                if count > 0:
                    parsed += stuffs + " "
                count += 1
            parsed = parsed.strip()
            for pots in pot:
                print(pots.get("name"))
                print(parsed)
                if str.lower(pots.get("name")) == str.lower(parsed):
                    print("dank weed")
                    line = "None"
                    while not line or line == "None":
                        line = text_model.make_sentence()
                    money = firebase.get('/Characters/'+user+'/Meta/money', None) - pots.get("saleCost")
                    if money > 0:
                        firebase.patch('/Characters/'+user+'/Meta/', {"money": money})
                        ite = firebase.get('/Characters/'+user+'/Inventory/', None)
                        if ite.get(parsed):
                            firebase.patch('/Characters/'+user+'/Inventory/', {parsed: ite.get(parsed)+1})
                        else:
                            firebase.put('/Characters/'+user+'/Inventory/', parsed, 1)
                        response = "You now have " + str(money)+" *CASHDOLLA*\nTrader: " + line
                    else:
                        response = "Trader: You don't have enough money you dumb fuck. " + line
        else:
            response = firebase.get('/Characters/'+ user + 'Meta/trader', None)
    elif command.startswith("drink"):
        stuff = command.split(" ")
        count = 0
        parsed = ""
        for stuffs in stuff:
            if count > 0:
                parsed += stuffs + " "
            count += 1
        parsed = parsed.strip() 
        num = firebase.get('/Characters/' + user + '/Inventory/' + parsed, None) 
        if num > 0:
            firebase.patch('/Characters/'+user+'/Inventory/', {parsed: num-1})
            health = firebase.get('/Characters/'+user+'/Attributes/health', None)
            maxhealth = firebase.get('/Characters/'+user+'/Attributes/maxhp', None)
            with open('config/items.json') as itemf:
                item = json.load(itemf)
            pot = item.get("Potions")
            for pots in pot:
                if str.lower(pots.get("name")) == str.lower(parsed):
                    health += pots.get("power")
                    if health > maxhealth:
                        firebase.patch('/Characters/'+user+'/Attributes/', {"health": maxhealth})
                    else:
                        firebase.patch('/Characters/'+user+'/Attributes/', {"health": health})
            response = "You have drunk pot"
        else:
            response = "You ate soylent"
    elif command.startswith("allocate"):
        stuff = command.split(" ")
        attr = stuff[1]
        points = int(stuff[2])
        curPoints = int(firebase.get('/Characters/'+user+'/Attributes/AllocationPoints',None))
        if attr not in ('charisma','dexterity','strength','intelligence','luck'):
            response = "Invalid attribute"
        elif curPoints < abs(points):
            response = "Invalid point amount"
        else:
            data = {attr:points, 'AllocationPoints':curPoints-points}
            firebase.patch('/Characters/'+user+'/Attributes',data)
            response = "You allocated " + str(points) + " to " + attr + "."
    elif command.startswith("stats"):
        attributes = firebase.get('/Characters/'+user+'/Attributes',None)
        name = firebase.get('/Characters/'+user+'/Name',None)
        response = "The character " + name + " has: Health: " + str(attributes.get('health')) + ", Strength: " + str(attributes.get('strength')) + ", Dexterity: " + str(attributes.get('dexterity')) + ", Intelligence: " + str(attributes.get('intelligence')) + ", Luck: " + str(attributes.get('luck'))
    elif command.startswith("money"):
        money = firebase.get('/Characters/'+user+'/Meta/money',None)
        response = "You have "+str(money)+" gold."
    elif command.startswith("help"):
        response = "/***********************************************************\n The commands: \n  adventure--- Starts a new adventure \n allocate--- spend attribute points on skils \n stats--- lists current attribute points an other character data \n money--- lists the amount of money you have \n whereami--- prints out the current location of character \n flee--- run from adventure \n attack--- attacks when on adventure"
    elif command.startswith("whereami"):
        meta = firebase.get('/Characters/'+user+'/Meta',None)
        location = meta.get('location')
        stage = meta.get('stage')
        if stage!=0:
            response="You're on an adventure near the town of " + location
        else:
            response = "You're in the town of "+location
    elif command.startswith("adventure"):
        meta = firebase.get('/Characters/'+user+'/Meta', None)
        stage = meta.get('stage')


        if meta.get('battle') != 'N/A':
            response = "You're in the middle of an adventure already!"
        elif stage == 0:
            chanceOfNothing = 15
            rng = random.randint(0,100)
            if rng <= chanceOfNothing:
                #########
                # Add flavor text stuff
                #########
                data = {'battle':'N/A', 'enemyHp':'N/A', 'stage':2}
                firebase.patch('/Characters/'+user+'/Meta',data)
                response = "Nothing happens"
            else:
                level = int(meta.get('level'))
                village = meta.get('location')
                monster = get_encounter(level,village)
                data = {'battle':monster, 'enemyHp':monster['health'], 'stage':1}
                firebase.patch('/Characters/'+user+'/Meta',data)
                response = "You encountered a "+monster['name']+" with "+ str(monster['health'])+" health. Use attack or flee."
    elif command.startswith("flee"):
        stage = firebase.get('/Characters/'+user+'/Meta/stage',None)
        if stage in (1,2,3):
            data = {'battle':'N/A', 'enemyHp':'N/A', 'stage':0}
            firebase.patch('/Characters/'+user+'/Meta',data)
            response = "You escaped safely back to " + firebase.get('/Characters/'+user+'/Meta/location',None)
        else:
            response = "You're already at the village!"
    elif command.startswith("loot"):
        response=gen_loot(1,user)
    elif command.startswith("wield"):
        item = command[6:]
        with open('config/items.json') as data_file:
            items = json.load(data_file)['Weapons']
        level = firebase.get('/Characters/'+user+'/Meta/level',None)
        inv = firebase.get('/Characters/'+user+'/Inventory',None)
        if item != "fists" and not inv.get(item):
            response = "You don't own that item!"
        elif items.get(item).get('power') > level:
            response = "You aren't powerful enough to wield that yet!"
        else:
            data={'weapon':item}
            firebase.patch('/Characters/'+user,data)
            response = "Equipped "+ item
    elif command.startswith("equip"):
        item = command[6:]
        with open('config/items.json') as data_file:
            items = json.load(data_file)['Armor']
        level = firebase.get('/Characters/'+user+'/Meta/level',None)
        inv = firebase.get('/Characters/'+user+'/Inventory',None)
        if item != "naked" and not inv.get(item):
            response = "You don't own that item!"
        elif items.get(item).get('defense') > level:
            response = "You aren't powerful enough to equip that yet!"
        else:
            data={'armor':item}
            firebase.patch('/Characters/'+user,data)
            response = "Equipped "+ item
    elif command.startswith("attack"):
        character = firebase.get('/Characters/'+user,None)
        armor = character.get('armor')
        weapon = character.get('weapon')
        health = character.get('Attributes').get('health')
        weapon, armor = get_equipment(weapon, armor)
        mCurHp = character.get('Meta').get('enemyHp')
        monster = character.get('Meta').get('battle')

        heroDmg = random.randint(weapon.get('min'),weapon.get('max'))
        critChance = character.get('Attributes').get('luck') + 100*weapon.get('crit')
        if random.randint(0,100) <= critChance:
            heroDmg = heroDmg * weapon.get('mod')
        heroDmg = heroDmg + math.floor(character.get('Attributes').get('strength') * .5)
        
        mDmg = random.randint(monster.get('min'),monster.get('max'))
        critChance = 100*monster.get('crit')
        if random.randint(0,100) <= critChance:
            mDmg = mDmg * monster.get('mod')

        heroDR = armor.get('defense')
        if mDmg >= heroDR:
            mDmg = mDmg - heroDR

        if character.get('Attributes').get('dexterity') >= math.floor(monster.get('power') * .5):
            mCurHp = mCurHp - heroDmg
            if mCurHp <= 0:
                stage = character.get('Meta').get('stage')
                print(stage)
                response = gen_loot(stage,user)
                if stage == 1:
                    #Beat stage 1
                    data = {'battle':'N/A', 'enemyHp':'N/A', 'stage':2}
                    firebase.patch('/Characters/'+user+'/Meta',data)
                    response = "You dealt " +str(heroDmg)+ " damage and killed the " + monster.get('name') +"! You are currently at "+str(health) + " health. "+ response + " Continue your adventure by saying 'adventure'"
                elif stage == 2:
                    #Beat stage 2
                    data = {'battle':'N/A', 'enemyHp':'N/A', 'stage':3}
                    firebase.patch('/Characters/'+user+'/Meta',data)
                    response = "You dealt " +str(heroDmg)+ " damage and killed the " + monster.get('name') +"! You are currently at "+str(health) + " health. "+ response + " Continue your adventure by saying 'adventure'"
                else:
                    #Beat the boss
                    data = {'battle':'N/A', 'enemyHp':'N/A', 'stage':0}
                    firebase.patch('/Characters/'+user+'/Meta',data)
                    response = "You dealt "+str(heroDmg)+" and beat " + monster.get('name') +"You are currently at "+str(health) + " health. "+ response
                    #####
                    #Find new town
                    #####
            else:
                health = health - mDmg
                if health <= 0:
                    response = new_user(character.get('Name'),user)
                else:
                    data = {'enemyHp':mCurHp}
                    firebase.patch('/Characters/'+user+'/Meta',data)
                    data = {'health':health}
                    firebase.patch('/Characters/'+user+'/Attributes',data)
                    ### Add critical hit flavor
                    response = "You dealt " + str(heroDmg) + " and received " + str(mDmg) + " damage. You are currently at " + str(health) + " health. " + monster.get('name') + " has " + str(mCurHp) + " health left."
        else:
            health = health - mDmg
            if health <= 0:
                response = new_user(character.get('Name'),user)
            else:
                mCurHp = mCurHp - heroDmg
                if mCurHp <= 0:
                    stage = character.get('Meta').get('stage')
                    print(stage)
                    response = gen_loot(stage,user)
                    if stage == 1:
                        #Beat stage 1
                        data = {'battle':'N/A', 'enemyHp':'N/A', 'stage':2}
                        firebase.patch('/Characters/'+user+'/Meta',data)
                        response = "You dealt " +str(heroDmg)+ " damage and killed the " + monster.get('name') +"! You are currently at "+str(health) + " health. "+ response + " Continue your adventure by saying 'adventure'"
                    elif stage == 2:
                        #Beat stage 2
                        data = {'battle':'N/A', 'enemyHp':'N/A', 'stage':3}
                        firebase.patch('/Characters/'+user+'/Meta',data)
                        response = "You dealt " +str(heroDmg)+ " damage and killed the " + monster.get('name') +"! You are currently at "+str(health) + " health. "+ response + " Continue your adventure by saying 'adventure'"
                    else:
                        #Beat the boss
                        data = {'battle':'N/A', 'enemyHp':'N/A', 'stage':0}
                        firebase.patch('/Characters/'+user+'/Meta',data)
                        response = "You dealt "+str(heroDmg)+" and beat " + monster.get('name') +"You are currently at "+str(health) + " health. "+ response
                        #####
                        #Find new town
                        #####
                else:
                    data = {'enemyHp':mCurHp}
                    firebase.patch('/Characters/'+user+'/Meta',data)
                    data = {'health':health}
                    firebase.patch('/Characters/'+user+'/Attributes',data)
                    ### Add critical hit flavor
                    response = "You dealt " + str(heroDmg) + " and received " + str(mDmg) + " damage. You are currently at " + str(health) + " health. " + monster.get('name') + " has " + str(mCurHp) + " health left."
        

        

    elif user == 'U4AD0NJ8L':
        response = "Lance stop being a fucking faggot"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def gen_loot(stage,user):
    if stage==1:
        luck = firebase.get('/Characters/'+user+'/Attributes/luck',None)
        if random.randint(0,100) <= luck:
            print("CHESTS")
            chestName = ""
            rng = random.randint(0,3)
            if rng == 0:
                chestName="Empty Chest"
            elif rng == 1:
                chestName = "Small Chest"
            elif rng == 2:
                chestName = "Medium Chest"
            elif rng == 3:
                chestName = "Gold Chest"
            quantity = 1
            temp = firebase.get('/Characters/'+user+'/Inventory/'+chestName, None)
            if temp:
                quantity = temp + 1
            data = {chestName:quantity}
            firebase.patch('/Characters/'+user+'/Inventory/',data)
            return "You got a "+chestName+"!"
        else:
            with open('config/items.json') as data_file:
                items = json.load(data_file)['Miscellaneous']
            item = items[random.randint(0,len(items)-1)]
            quantity = 1
            temp = firebase.get('/Characters/'+user+'/Inventory/'+item.get('name'), None)
            if temp:
                quantity = temp + 1
            print(quantity)
            data = {item.get('name'):quantity}
            firebase.patch('/Characters/'+user+'/Inventory/',data)
            return "You found a "+item.get('name')+"!"

def new_user(name, user):
    data = {'Name':name, 'Meta':{'level':1, 'exp':0, 'money':0, 'battle':'N/A', 'enemyHp':'N/A', 'stage':0, 'location':'Dire Village','trader': 'general manager'}, 'armor': 'naked', 'Attributes': {'charisma': 0, 'dexterity': 0, 'health': 10, 'intelligence': 0, 'luck': 0, 'strength': 0, 'AllocationPoints':5, 'maxhp':10}, 'Inventory': {'soylent': 1}, 'weapon': 'fists'}    
    result = firebase.put('/Characters',user,data)
    return "You, "+name+", wake up on the floor of the tavern, extremely hungover, with not a penny to your name. What would you like to do?"

def get_equipment(weaponName, armorName):
    with open('config/items.json') as data_file:    
        weapons = json.load(data_file)['Weapons']
    with open('config/items.json') as data_file2:
        armors = json.load(data_file2)['Armor']
    weapon = weapons.get(weaponName)
    armor = armors.get(armorName)
    return weapon, armor

def get_encounter(level, village):
    weights = [1, 4, 13, 40, 121, 364, 1093, 3280, 9841, 29524]
    rng = random.randint(1,weights[level-1])
    mlvl = 0
    for i in range(0,10):
        if rng <= weights[i]:
            mlvl=i+1
            break
    with open('config/enemies.json') as data_file:    
        monsters = json.load(data_file)[village][(str(mlvl))]
    rng = random.randint(0,len(monsters)-1)
    return monsters[rng]

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return (output['text'].split(AT_BOT)[1].strip().lower(), output['channel'], output['user'])
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            stuff = parse_slack_output(slack_client.rtm_read())
            if stuff[0] and stuff[1] and stuff[2]:
                print(stuff[0])
                #print(stuff[1])
                #print(stuff[2])
                handle_command(stuff[0], stuff[1], stuff[2])
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")