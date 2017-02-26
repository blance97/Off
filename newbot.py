import os
import time
import json
from slackclient import SlackClient
from firebase import firebase

firebase = firebase.FirebaseApplication('https://slackbotadventures.firebaseio.com/', None)


# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")
BOT_ID = 'U4AA1UYN7'

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
slack_client = SlackClient('xoxb-146341984755-1fYi3Oau3Cx262xcxP3Tzzp0')


def handle_command(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    if command.startswith("get"):
        name = command.split(" ")
        parsed = '/'
        for part in name:
            if part != 'get':
                parsed = parsed + part + '/'
        result = firebase.get(parsed, None)
        response = result
    elif command.startswith("post"):
        stuff = command.split(" ")
        parsed = '/'
        count = 0
        for part in stuff:
            if count > 1:
                parsed = parsed + part + '/'
            count += 1
        firebase.post(parsed, stuff[1])
        response = 'succeeded'
    elif command.startswith("put"):
        stuff = command.split(" ")
        parsed = '/'
        count = 0
        for part in stuff:
            if count > 2:
                parsed = parsed + part + '/'
            count += 1
        firebase.put(parsed, stuff[1], stuff[2])
    elif command.startswith("patch"):
        stuff = command.split(" ")
        parsed = '/'
        count = 0
        for part in stuff:
            if count > 1:
                parsed = parsed + part + '/'
            count += 1
        firebase.patch(parsed, stuff[1])
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


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