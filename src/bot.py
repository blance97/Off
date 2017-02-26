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
slack_client = SlackClient('xoxb-146341984755-A3A7fjqsQ3v4Cj28DSgVughA')


def handle_command(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    if command.startswith("newchar"):
        response = new_user(command.split(" ")[1], user)
    elif command.startswith("tradelist"):
        if firebase.get('/Characters/' + user + '/Meta/trader', None) == "general manager":
            with open('config/items.json') as itemf:
                item = json.load(itemf)
            pot = item.get("Potions")
            response = "/*******************TRADE LIST*********************"
            for pots in pot:
                response += "\n*" + \
                    pots.get("name") + "*-------------" + \
                    str(pots.get("saleCost"))
            response += "\nYou have $$$" + \
                str(firebase.get('/Characters/' + user +
                                 '/Meta/money', None)) + " *cash DOLLA*"
        else:
            response = firebase.get(
                '/Characters/' + user + 'Meta/trader', None)
    elif command.startswith("buy"):
        stuff = command.split(' ')
        if firebase.get('/Characters/' + user + '/Meta/trader', None) == "general manager" and firebase.get('/Characters/' + user + '/Meta/stage', None) == 0:
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
                if str.lower(pots.get("name")) == str.lower(parsed):
                    line = "None"
                    while not line or line == "None":
                        line = text_model.make_sentence()
                    money = firebase.get(
                        '/Characters/' + user + '/Meta/money', None) - pots.get("saleCost")
                    if money > 0:
                        firebase.patch('/Characters/' + user +
                                       '/Meta/', {"money": money})
                        ite = firebase.get(
                            '/Characters/' + user + '/Inventory/', None)
                        if ite.get(parsed):
                            firebase.patch(
                                '/Characters/' + user + '/Inventory/', {parsed: ite.get(parsed) + 1})
                        else:
                            firebase.put('/Characters/' + user +
                                         '/Inventory/', parsed, 1)
                        response = "You now have " + \
                            str(money) + " *CASHDOLLA*\nTrader: _" + line + "_"
                    else:
                        response = "Trader: You don't have enough money. _" + line + "_"
        else:
            response = 'You can\'t trade here'
    elif command.startswith("sell"):
        stuff = command.split(' ')
        if firebase.get('/Characters/' + user + '/Meta/trader', None) == "general manager" and firebase.get('/Characters/' + user + '/Meta/stage', None) == 0:
            with open('config/items.json') as itemf:
                item = json.load(itemf)
            response = "/*******************TRADE LIST*********************"
            count = 0
            parsed = ""
            for stuffs in stuff:
                if count > 0:
                    parsed += stuffs + " "
                count += 1
            parsed = parsed.strip()
            pot = item.get("Potions")
            misc = item.get("Miscellaneous")
            armor = item.get("Armor")
            weapon = item.get("Weapons")
            for pots in pot:
                if str.lower(pots.get("name")) == str.lower(parsed):
                    line = "None"
                    while not line or line == "None":
                        line = text_model.make_sentence()
                    money = firebase.get(
                        '/Characters/' + user + '/Meta/money', None) + pots.get("saleCost")
                    ite = firebase.get(
                        '/Characters/' + user + '/Inventory/', None)
                    if ite.get(parsed) == 1:
                        firebase.delete('/Characters/' +
                                        user + '/Inventory/', parsed)
                        firebase.patch('/Characters/' + user +
                                   '/Meta/', {"money": money})
                    elif ite.get(parsed):
                        firebase.patch(
                            '/Characters/' + user + '/Inventory/', {parsed: ite.get(parsed) - 1})
                        firebase.patch('/Characters/' + user +
                            '/Meta/', {"money": money})
                    else:
                        response = "Trader: _You don't have enough items. " + line + "_"
                    response = "You now have " + \
                        str(money) + " *CASHDOLLA*\nTrader: _" + line + "_"

            for miscs in misc:
                if str.lower(miscs.get("name")) == str.lower(parsed):
                    line = "None"
                    while not line or line == "None":
                        line = text_model.make_sentence()
                    money = firebase.get(
                        '/Characters/' + user + '/Meta/money', None) + miscs.get("saleCost")
                    ite = firebase.get(
                        '/Characters/' + user + '/Inventory/', None)
                    if ite.get(parsed) == 1:
                        firebase.delete('/Characters/' +
                                        user + '/Inventory/', parsed)
                        firebase.patch('/Characters/' + user +
                                   '/Meta/', {"money": money})
                    elif ite.get(parsed):
                        firebase.patch(
                            '/Characters/' + user + '/Inventory/', {parsed: ite.get(parsed) - 1})
                        firebase.patch('/Characters/' + user +
                                   '/Meta/', {"money": money})
                    else:
                        response = "Trader: _You don't have enough items. " + line + "_"
                    response = "You now have " + \
                        str(money) + " *CASHDOLLA*\nTrader: _" + line + "_"
            for armors in armor:
                aval = armor[armors]
                if str.lower(armors) == str.lower(parsed):
                    line = "None"
                    while not line or line == "None":
                        line = text_model.make_sentence()
                    money = firebase.get(
                        '/Characters/' + user + '/Meta/money', None) + aval.get("saleCost")
                    ite = firebase.get(
                        '/Characters/' + user + '/Inventory/', None)
                    if ite.get(parsed) == 1:
                        if firebase.get('/Characters/' + user + '/armor', None) == parsed:
                            response = "You can't sell your equipped armor"
                        else:
                            firebase.delete('/Characters/' +
                                            user + '/Inventory/', parsed)
                            firebase.patch('/Characters/' + user +
                                   '/Meta/', {"money": money})
                            response = "You now have " + \
                                str(money) + " *CASHDOLLA*\nTrader: _" + line + "_"
                    elif ite.get(parsed):
                        firebase.patch(
                            '/Characters/' + user + '/Inventory/', {parsed: ite.get(parsed) - 1})
                        firebase.patch('/Characters/' + user +
                                   '/Meta/', {"money": money})
                        response = "You now have " + \
                            str(money) + " *CASHDOLLA*\nTrader: _" + line + "_"
                    else:
                        response = "Trader: _You don't have enough items. " + line + "_"
 
            for weaps in weapon:
                wval = weapon[weaps]
                if str.lower(weaps) == str.lower(parsed):
                    line = "None"
                    while not line or line == "None":
                        line = text_model.make_sentence()
                    money = firebase.get(
                        '/Characters/' + user + '/Meta/money', None) + wval.get("saleCost")
                    ite = firebase.get(
                        '/Characters/' + user + '/Inventory/', None)
                    if ite.get(parsed) == 1:
                        print(firebase.get('/Characters/' +
                                           user + '/weapon', None) == parsed)
                        print(parsed)
                        if firebase.get('/Characters/' + user + '/weapon', None) == parsed:
                            response = "You can't sell your equipped weapon"
                        else:
                            firebase.delete('/Characters/' +
                                            user + '/Inventory/', parsed)
                            firebase.patch('/Characters/' + user +
                                   '/Meta/', {"money": money})
                            response = "You now have " + \
                                str(money) + " *CASHDOLLA*\nTrader: _" + line + "_"
                    elif ite.get(parsed):
                        firebase.patch(
                            '/Characters/' + user + '/Inventory/', {parsed: ite.get(parsed) - 1})
                        firebase.patch('/Characters/' + user +
                                   '/Meta/', {"money": money})
                        response = "You now have " + \
                            str(money) + " *CASHDOLLA*\nTrader: _" + line + "_"
                    else:
                        response = "Trader: _You don't have enough items. " + line + "_"
        else:
            response = 'You can\'t trade here'
    elif command.startswith("drink"):
        stuff = command.split(" ")
        count = 0
        parsed = ""
        for stuffs in stuff:
            if count > 0:
                parsed += stuffs + " "
            count += 1
        parsed = parsed.strip()
        num = firebase.get('/Characters/' + user +
                           '/Inventory/' + parsed, None)
        if num > 0:
            firebase.patch('/Characters/' + user +
                           '/Inventory/', {parsed: num - 1})
            health = firebase.get('/Characters/' + user +
                                  '/Attributes/health', None)
            maxhealth = firebase.get(
                '/Characters/' + user + '/Attributes/maxhp', None)
            with open('config/items.json') as itemf:
                item = json.load(itemf)
            pot = item.get("Potions")
            for pots in pot:
                if str.lower(pots.get("name")) == str.lower(parsed):
                    health += pots.get("power")
                    if health > maxhealth:
                        firebase.patch('/Characters/' + user +
                                       '/Attributes/', {"health": maxhealth})
                    else:
                        firebase.patch('/Characters/' + user +
                                       '/Attributes/', {"health": health})
            response = "You have drunk " + parsed
        else:
            response = "That doesn't exist"
    elif command.startswith("allocate"):
        stuff = command.split(" ")
        attr = stuff[1]
        points = int(stuff[2])
        curPoints = int(firebase.get('/Characters/' + user +
                                     '/Attributes/AllocationPoints', None))
        if attr not in ('charisma', 'dexterity', 'strength', 'intelligence', 'luck'):
            response = "Invalid attribute"
        elif curPoints < abs(points) or points < 0:
            response = "Invalid point amount"
        elif curPoints + points > 15:
            print(curPoints)
            print(points)
            response = "Max 15 points are allowed per attribute"
        else:
            data = {attr: points, 'AllocationPoints': curPoints - points}
            firebase.patch('/Characters/' + user + '/Attributes', data)
            response = "You allocated " + str(points) + " to " + attr + "."
    elif command.startswith("stats"):
        attributes = firebase.get('/Characters/' + user + '/Attributes', None)
        name = firebase.get('/Characters/' + user + '/Name', None)
        response = "The character " + name + " has: Health: " + str(attributes.get('health')) + ", Strength: " + str(attributes.get('strength')) + ", Dexterity: " + str(
            attributes.get('dexterity')) + ", Intelligence: " + str(attributes.get('intelligence')) + ", Luck: " + str(attributes.get('luck'))
    elif command.startswith("money"):
        money = firebase.get('/Characters/' + user + '/Meta/money', None)
        response = "You have " + str(money) + " gold."
    elif command.startswith("help"):
        response = "/***********************************************************\n The commands: \n  adventure--- Starts a new adventure \n allocate--- spend attribute points on skils \n stats--- lists current attribute points an other character data \n attack--- If your character is in an encounter with an enemy, this command will allow you to start attacking. In each attack, both the character and the enemy will attack in an order decided on by luck. \n buy--- Use buy to purchase items from the general manager in the village. \n drink--- Use this command to drink potions to increase your character's health. \n equip---  Changes your current armor to another specified armor in your inventory.\n exp--- Allows you to see your experience points and allocation points. \n flee--- If your character has encountered an enemy, this command will allow you to flee back to the village. By doing this, you will be reset back to stage 0 or your current adventure. \n help--- This command will print a list of all commands you can use in the game. \n inventory---  Allows you to see all the items in your invetory.\n money--- This will return the amount of money you currently have in your inventory. \n newChar ---  Creates a new character for your username. Each Slack user can have multiple characters, each is stored in firebase with it's information. \n Sell--- This allows you to sell an item from your inventory to the general manager in the village. \n stats--- Will display your character's attributes.\n tradelist--- This will shows the items the general manager has to sell in the town.\n wield--- Changes your current weapon to another specified weapon in your inventory.\n whereami--- Tells you which village you had previously visited. This also specifies the pack of enemies in this area."
    elif command.startswith("whereami"):
        meta = firebase.get('/Characters/' + user + '/Meta', None)
        location = meta.get('location')
        stage = meta.get('stage')
        if stage != 0:
            response = "You're on an adventure near the town of " + location
        else:
            response = "You're in the town of "+location
    elif command.startswith("inventory"):
        inv = firebase.get('/Characters/'+user+'/Inventory', None)
        response = inv
    elif command.startswith("adventure"):
        meta = firebase.get('/Characters/' + user + '/Meta', None)
        stage = meta.get('stage')

        if meta.get('battle') != 'N/A':
            response = "You're in the middle of an adventure already!"
        elif stage == 0:
            chanceOfNothing = 15
            rng = random.randint(0, 100)
            if rng <= chanceOfNothing:
                #########
                # Add flavor text stuff
                #########
                data = {'battle':'N/A', 'enemyHp':'N/A', 'stage':1}
                firebase.patch('/Characters/'+user+'/Meta',data)
                response = "Nothing happens"
            else:
                level = int(meta.get('level'))
                village = meta.get('location')
                monster = get_encounter(level,village,"normal")
                data = {'battle':monster, 'enemyHp':monster['health'], 'stage':1}
                firebase.patch('/Characters/'+user+'/Meta',data)
                response = "You encountered a "+monster['name']+" with "+ str(monster['health'])+" health. Use attack or flee."
        elif stage==1:
            data = {'battle':'N/A', 'enemyHp':'N/A', 'stage':2}
            firebase.patch('/Characters/'+user+'/Meta',data)
            rng = random.randint(0,100)
            if rng <= 15:
                #Nothing
                response = "Nothing happens"
            elif rng <=50:
                #Regular encounter
                level = int(meta.get('level'))
                village = meta.get('location')
                monster = get_encounter(level,village,"normal")
                data = {'battle':monster, 'enemyHp':monster['health']}
                firebase.patch('/Characters/'+user+'/Meta',data)
                response = "You encountered a "+monster['name']+" with "+ str(monster['health'])+" health. Use attack or flee."
            elif rng <= 75:
                #Hideout
                level = int(meta.get('level'))
                village = meta.get('location')
                monster = get_encounter(level,village,"normal")
                data = {'battle':monster, 'enemyHp':monster['health'], 'hideout':True}
                firebase.patch('/Characters/'+user+'/Meta',data)
                response = "You come upon the " + monster['name'] + " hideout and are attacked by one of them with "+ str(monster['health'])+" health. Use attack or flee."
            else:
                #Trap
                level = int(meta.get('level'))
                village = meta.get('location')
                monster = get_encounter(level,village,"normal")
                weaponName = firebase.get('/Characters/'+user+'/weapon', None)
                if weaponName != "fists":
                    data = {'battle':monster, 'enemyHp':monster['health'], 'dropWep':weaponName}
                    firebase.patch('/Characters/'+user+'/Meta',data)
                    data = {'weapon':'fists'}
                    firebase.patch('/Characters/'+user,data)

                    quantity = firebase.get('/Characters/'+user+'/Inventory/'+weaponName, None)
                    if quantity > 1:
                        data = {weaponName:quantity-1}
                        firebase.patch('/Characters/'+user+'/Inventory',data)
                    else:
                        firebase.delete('/Characters/'+user+'/Inventory',weaponName)

                    response = "Walking through the area, you fall into a " + monster['name'] + " trap! You drop your weapon and must fend for yourself! A " + monster['name'] + " with " + str(monster['health']) + " health charges at you."
                else:
                    health = firebase.get('/Characters/'+user+'/Attributes/health',None)
                    health = health - level
                    if health <= 0:
                        death = new_user(character.get('Name'),user)
                        response = "While walking through the area you fell into a trap and died. " + death
                    else:
                        data = {'health':health}
                        firebase.patch('/Characters/'+user+'/Attributes',data)
                        response = "Walking through the area, you fall into a " + monster['name'] + " trap! You fall and lose "+str(level)+" health! You currently have "+str(health)+" health. A " + monster['name']+ " with " + str(monster['health']) +" charges at you."
        elif stage==2:
            data = {'battle':'N/A', 'enemyHp':'N/A', 'stage':3}
            firebase.patch('/Characters/'+user+'/Meta',data)
            rng = random.randint(0,100)
            print(rng)
            if rng <= 70:
                #boss battle
                level = int(meta.get('level'))
                village = meta.get('location')
                monster = get_encounter(level,village,"boss")
                data = {'battle':monster, 'enemyHp':monster['health']}
                firebase.patch('/Characters/'+user+'/Meta',data)
                response = "Up ahead you see a castle, inside you encounter "+monster['name']+" with "+ str(monster['health'])+" health. Use attack or flee."
            elif rng <= 85:
                #unguarded treasure
                meta = firebase.get('/Characters/'+user+'/Meta',None)
                level = meta.get('level')
                money = meta.get('money')
                goldrng = random.randint(2*level,5*level)
                data = {'money':money+goldrng}
                firebase.patch('/Characters/'+user+'/Meta',data)
                r1 = gen_loot(2,user)
                r2 = gen_loot(2,user)
                response = "You stumble upon a pile of unguarded treasure! "+ r1 + r2 + " In the back you see a pile of " + goldrng + " gold!"
            else:
                #nothing
                response = "You return to the village without anything more happening."
                data = {'battle':'N/A', 'enemyHp':'N/A', 'stage':0}
                firebase.patch('/Characters/'+user+'/Meta',data)

    elif command.startswith("flee"):
        stage = firebase.get('/Characters/'+user+'/Meta/stage',None)
        if stage in (1,2,3):
            if firebase.get('/Characters/'+user+'/Meta/dropWep',None) != 'N/A':
                data = {'battle':'N/A', 'enemyHp':'N/A', 'stage':0, 'dropWep':'N/A', 'hideout':False}
                firebase.patch('/Characters/'+user+'/Meta',data)
                response = "You escaped safely back to " + firebase.get('/Characters/'+user+'/Meta/location',None) +". But you left your weapon behind."
            else:
                data = {'battle':'N/A', 'enemyHp':'N/A', 'stage':0, 'hideout':False}
                firebase.patch('/Characters/'+user+'/Meta',data)
                response = "You escaped safely back to " + firebase.get('/Characters/'+user+'/Meta/location',None)
        else:
            response = "You're already at the village!"
    elif command.startswith("exp"):
        exp = firebase.get('/Characters/'+user+'/Meta/exp',None)
        ap = firebase.get('/Characters/'+user+'/Attributes/AllocationPoints',None)
        response="You have " + str(exp) + " experience points! You have " + str(ap) + " skill points to spend!"
    elif command.startswith("travel"):
        meta = firebase.get('/Characters/'+user+'/Meta',None)
        level = meta.get('level')
        bossKill = meta.get('bossKill')
        location = meta.get('location')
        if level < 5 or not bossKill:
            response = "You must be level 5 and have defeated a boss to travel"
        else:
            if location == 'Dire Village':
                data = {'location':'Memetown'}
                firebase.patch('/Characters/'+user+'/Meta',data)
                response = "You are now at Memetown, land of the dankest of memes"
            else:
                data = {'location':'Dire Village'}
                firebase.patch('/Characters/'+user+'/Meta',data)
                response = "Welcome back to Dire Village"

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
        monster = character.get('Meta').get('battle')
        if monster == 'N/A':
            response = "You're in the village!"
        else:
            armor = character.get('armor')
            weapon = character.get('weapon')
            health = character.get('Attributes').get('health')
            weapon, armor = get_equipment(weapon, armor)
            mCurHp = character.get('Meta').get('enemyHp')

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
                    temp = firebase.get('/Characters/'+user+'/Meta/dropWep',None)
                    if temp != 'N/A':
                        data = {'dropWep':'N/A'}
                        firebase.patch('/Characters/'+user+'/Meta',data)
                        quantity = firebase.get('/Characters/'+user+'/Inventory/'+temp, None)
                        if not quantity:
                            data = {temp:1}
                            firebase.patch('/Characters/'+user+'/Inventory',data)
                        else:
                            data = {temp:quantity+1}
                            firebase.patch('/Characters/'+user+'/Inventory',data)

                    curXP = character.get('Meta').get('exp')
                    exps = [5,7,10,14,19,25,32,40,49,59,70,82,95,109,124]
                    goals = [15, 43, 83, 153, 253, 400, 650, 1050, 1550, 2500, 4000, 6000, 9000, 13000, 18000]
                    gain = exps[monster.get('power')-1]
                    if stage==3:
                        gain = gain * 2
                    curXP = curXP + gain
                    curLevel = character.get('Meta').get('level')
                    data = {'exp':curXP}
                    firebase.patch('/Characters/'+user+'/Meta',data)
                    if curXP >= goals[curLevel-1]:
                        #Level up
                        data = {'level':curLevel+1}
                        firebase.patch('/Characters/'+user+'/Meta',data)
                        ap = character.get('Attributes').get('AllocationPoints')
                        maxhp = character.get('Attributes').get('maxhp')
                        data = {'AllocationPoints':ap+5, 'health':maxhp+10, 'maxhp':maxhp+10}
                        firebase.patch('/Characters/'+user+'/Attributes',data)
                        slack_client.api_call("chat.postMessage", channel=channel,
                            text="You've leveled up to level "+str(curLevel+1)+"! Use allocate to spend your skill points!", as_user=True)

                    response = gen_loot(stage,user)
                    if stage == 1:
                        #Beat stage 1
                        response = "You dealt " +str(heroDmg)+ " damage and killed the " + monster.get('name') +"! You are currently at "+str(health) + " health. "+ response + " Continue your adventure by saying 'adventure'"
                        data = {'battle':'N/A', 'enemyHp':'N/A'}
                        firebase.patch('/Characters/'+user+'/Meta',data)
                    elif stage == 2:
                        #Beat stage 2
                        response = "You dealt " +str(heroDmg)+ " damage and killed the " + monster.get('name') +"! You are currently at "+str(health) + " health. "+ response + " Continue your adventure by saying 'adventure'"
                        data = {'battle':'N/A', 'enemyHp':'N/A'}
                        firebase.patch('/Characters/'+user+'/Meta',data)
                    else:
                        #Beat the boss
                        response = "You dealt "+str(heroDmg)+" and beat " + monster.get('name') +" You are currently at "+str(health) + " health. "+ response
                        data = {'battle':'N/A', 'enemyHp':'N/A', 'stage':0, 'bossKill':True}
                        firebase.patch('/Characters/'+user+'/Meta',data)
                        #####
                        # Find new town
                        #####
                else:
                    health = health - mDmg
                    if health <= 0:
                        response = new_user(character.get('Name'),user)
                    else:
                        response = "You dealt " + str(heroDmg) + " and received " + str(mDmg) + " damage. You are currently at " + str(health) + " health. " + monster.get('name') + " has " + str(mCurHp) + " health left."
                        data = {'enemyHp':mCurHp}
                        firebase.patch('/Characters/'+user+'/Meta',data)
                        data = {'health':health}
                        firebase.patch('/Characters/'+user+'/Attributes',data)
                        ### Add critical hit flavor
            else:
                health = health - mDmg
                if health <= 0:
                    response = new_user(character.get('Name'),user)
                else:
                    mCurHp = mCurHp - heroDmg
                    if mCurHp <= 0:
                        stage = character.get('Meta').get('stage')
                        temp = firebase.get('/Characters/'+user+'/Meta/dropWep',None)
                        if temp != 'N/A':
                            quantity = firebase.get('/Characters/'+user+'/Inventory/'+temp, None)
                            if not quantity:
                                data = {temp:1}
                                firebase.patch('/Characters/'+user+'/Inventory',data)
                            else:
                                data = {temp:quantity+1}
                                firebase.patch('/Characters/'+user+'/Inventory',data)
                                
                        curXP = character.get('Meta').get('exp')
                        exps = [5,7,10,14,19,25,32,40,49,59,70,82,95,109,124]
                        goals = [15, 43, 83, 153, 253, 400, 650, 1050, 1550, 2500, 4000, 6000, 9000, 13000, 18000]
                        gain = exps[monster.get('power')-1]
                        if stage==3:
                            gain = gain * 2
                        curXP = curXP + gain
                        curLevel = character.get('Meta').get('level')
                        data = {'exp':curXP}
                        firebase.patch('/Characters/'+user+'/Meta',data)
                        if curXP >= goals[curLevel-1]:
                            #Level up
                            data = {'level':curLevel+1}
                            firebase.patch('/Characters/'+user+'/Meta',data)
                            ap = character.get('Attributes').get('AllocationPoints')
                            maxhp = character.get('Attributes').get('maxhp')
                            data = {'AllocationPoints':ap+5, 'health':maxhp+10, 'maxhp':maxhp+10}
                            firebase.patch('/Characters/'+user+'/Attributes',data)
                            slack_client.api_call("chat.postMessage", channel=channel,
                                text="You've leveled up to level "+str(curLevel+1)+"! Use allocate to spend your skill points!", as_user=True)

                        response = gen_loot(stage,user)
                        if stage == 1:
                            #Beat stage 1
                            response = "You dealt " +str(heroDmg)+ " damage and killed the " + monster.get('name') +"! You are currently at "+str(health) + " health. "+ response + " Continue your adventure by saying 'adventure'"
                            data = {'battle':'N/A', 'enemyHp':'N/A'}
                            firebase.patch('/Characters/'+user+'/Meta',data)
                        elif stage == 2:
                            #Beat stage 2
                            response = "You dealt " +str(heroDmg)+ " damage and killed the " + monster.get('name') +"! You are currently at "+str(health) + " health. "+ response + " Continue your adventure by saying 'adventure'"
                            data = {'battle':'N/A', 'enemyHp':'N/A'}
                            firebase.patch('/Characters/'+user+'/Meta',data)
                        else:
                            #Beat the boss
                            response = "You dealt "+str(heroDmg)+" and beat " + monster.get('name') +" You are currently at "+str(health) + " health. "+ response
                            data = {'battle':'N/A', 'enemyHp':'N/A', 'stage':0, 'bossKill':True}
                            firebase.patch('/Characters/'+user+'/Meta',data)
                            #####
                            #Find new town
                            #####
                    else:
                        response = "You dealt " + str(heroDmg) + " and received " + str(mDmg) + " damage. You are currently at " + str(health) + " health. " + monster.get('name') + " has " + str(mCurHp) + " health left."
                        data = {'enemyHp':mCurHp}
                        firebase.patch('/Characters/'+user+'/Meta',data)
                        data = {'health':health}
                        firebase.patch('/Characters/'+user+'/Attributes',data)
                        ### Add critical hit flavor
            

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
            rng = random.randint(0, 3)
            if rng == 0:
                chestName = "Empty Chest"
            elif rng == 1:
                chestName = "Small Chest"
            elif rng == 2:
                chestName = "Medium Chest"
            elif rng == 3:
                chestName = "Gold Chest"
            quantity = 1
            temp = firebase.get('/Characters/' + user +
                                '/Inventory/' + chestName, None)
            if temp:
                quantity = temp + 1
            data = {chestName: quantity}
            firebase.patch('/Characters/' + user + '/Inventory/', data)
            return "You got a " + chestName + "!"
        else:
            with open('config/items.json') as data_file:
                items = json.load(data_file)['Miscellaneous']
            item = items[random.randint(0,len(items)-1)]
            quantity = 1
            temp = firebase.get('/Characters/' + user +
                                '/Inventory/' + item.get('name'), None)
            if temp:
                quantity = temp + 1
            data = {item.get('name'):quantity}
            firebase.patch('/Characters/'+user+'/Inventory/',data)
            return "You found a "+item.get('name')+"!"
    elif stage==2:
        if firebase.get('/Characters/'+user+'/Meta/hideout', None) == True:
            data = {'hideout':False}
            firebase.patch('/Characters/'+user+'/Meta',data)
            rng = random.randint(0,1)
            print(rng)
            if rng == 0:
                #weapon
                with open('config/items.json') as data_file:
                    items = json.load(data_file)['Weapons']
                lst = list(items.keys())
                rng = random.randint(0,len(lst)-1)
                wep = items.get(lst[rng])
                level = firebase.get('/Characters/'+user+'/Meta/level', None)
                print(wep)
                print(lst[rng])
                print(wep.get('power') > level + 2)
                while wep.get('power') > level + 2 or lst[rng] == 'fists':
                    print(rng)
                    rng = (rng+1)%len(lst)
                    wep = items.get(lst[rng])
                quantity = 1
                temp = firebase.get('/Characters/'+user+'/Inventory/'+lst[rng], None)
                if temp:
                    quantity = temp + 1
                data = {lst[rng]:quantity}
                firebase.patch('/Characters/'+user+'/Inventory/',data)
                return "You found " + lst[rng]+"!"
            else:
                #armor
                with open('config/items.json') as data_file:
                    items = json.load(data_file)['Armor']
                lst = list(items.keys())
                rng = random.randint(0,len(lst)-1)
                wep = items.get(lst[rng])
                level = firebase.get('/Characters/'+user+'/Meta/level',None)
                print(wep)
                print(lst[rng])
                print(wep.get('defense') > level + 2)
                while wep.get('defense') > level + 2 or lst[rng] == 'naked':
                    print(rng)
                    rng = (rng+1)%len(lst)
                    wep = items.get(lst[rng])
                quantity = 1
                temp = firebase.get('/Characters/'+user+'/Inventory/'+lst[rng], None)
                print(temp)
                if temp:
                    quantity = temp + 1
                data = {lst[rng]:quantity}
                firebase.patch('/Characters/'+user+'/Inventory/',data)
                return "You found " + lst[rng]+"!"
        meta = firebase.get('/Characters/'+user+'/Meta',None)
        level = meta.get('level')
        money = meta.get('money')
        goldrng = random.randint(2*level,5*level)
        data = {'money':money+goldrng}
        firebase.patch('/Characters/'+user+'/Meta',data)
        return "You found " + str(goldrng) + " gold!"
    elif stage==3:
        meta = firebase.get('/Characters/'+user+'/Meta',None)
        level = meta.get('level')
        money = meta.get('money')
        goldrng = random.randint(10*level,15*level)
        data = {'money':money+goldrng}
        firebase.patch('/Characters/'+user+'/Meta',data)
        return "You found a massive treasure trove of " + str(goldrng) + " gold!"
        

def new_user(name, user):
    data = {'Name':name, 'Meta':{'level':1, 'exp':0, 'money':0, 'battle':'N/A', 'enemyHp':'N/A', 'stage':0, 'location':'Dire Village','trader': 'general manager','hideout':False, 'dropWep':'N/A', 'bossKill':False}, 'armor': 'naked', 'Attributes': {'charisma': 0, 'dexterity': 0, 'health': 10, 'intelligence': 0, 'luck': 0, 'strength': 0, 'AllocationPoints':5, 'maxhp':10}, 'Inventory': {'soylent': 1}, 'weapon': 'fists'}    
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

def get_encounter(level, village,encType):
    weights = [1, 4, 13, 40, 121, 364, 1093, 3280, 9841, 29524]
    rng = random.randint(1, weights[level - 1])
    mlvl = 0
    for i in range(0, 10):
        if rng <= weights[i]:
            mlvl = i + 1
            break
    with open('config/enemies.json') as data_file:    
        monsters = json.load(data_file)[village]
    if encType=="boss":
        return monsters.get('Bosses')[mlvl-1]
    else:
        monsters = monsters[(str(mlvl))]
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
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            stuff = parse_slack_output(slack_client.rtm_read())
            if stuff[0] and stuff[1] and stuff[2]:
                # if stuff[2] != 'U4AD0NJ8L':
                    # print(stuff[0])
                    #print(stuff[1])
                    #print(stuff[2])
                    handle_command(stuff[0], stuff[1], stuff[2])
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
