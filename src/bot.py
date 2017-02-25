import os
import time
import json
import random
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
slack_client = SlackClient('xoxb-146341984755-iSkNDwRRKTFM4S4a78YjCkSk')


def handle_command(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    if command.startswith("newchar"):
        name = command.split(" ")[1]
        data = {'Name':name, 'Meta':{'level':1, 'exp':0, 'money':0, 'battle':'N/A', 'enemyHp':'N/A', 'stage':0, 'location':'Dire Village', 'trader': 'general manager'}, 'Armor': {'arm': 'Naked'}, 'Attributes': {'charisma': 0, 'dexterity': 0, 'health': 10, 'intelligence': 0, 'luck': 0, 'strength': 0, 'AllocationPoints':5}, 'Inventory': {'item': 'soylent'}, 'Weapon': {'wep': 'Fists'}}    
        result = firebase.put('/Characters',user,data)
        response = "You, "+name+", wake up on the floor of the tavern, extremely hungover, with not a penny to your name. What would you like to do?"
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
        print(attributes.get('strength'))
        response = "The character " + name + " has: Health: " + str(attributes.get('health')) + ", Strength: " + str(attributes.get('strength')) + ", Dexterity: " + str(attributes.get('dexterity')) + ", Intelligence: " + str(attributes.get('intelligence')) + ", Luck: " + str(attributes.get('luck'))
    elif command.startswith("money"):
        money = firebase.get('/Characters/'+user+'/Meta/money',None)
        response = "You have "+str(money)+" gold."
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

        if stage == 0:
            chanceOfNothing = 15
            rng = random.randint(0,100)
            if rng <= chanceOfNothing:
                #########
                # Add flavor text stuff
                #########
                response = "Nothing happens"
            else:
                level = int(meta.get('level'))
                village = meta.get('location')
                monster = get_encounter(level,village)
                data = {'battle':monster, 'enemyHp':monster['health']}
                firebase.patch('/Characters/'+user+'/Meta',data)
                response = "You encountered a "+monster['name']+" with "+ str(monster['health'])+" health."

    elif user == 'U4AD0NJ8L':
        response = "Lance stop being a fucking faggot"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


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
                print(stuff[1])
                print(stuff[2])
                handle_command(stuff[0], stuff[1], stuff[2])
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")