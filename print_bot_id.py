"""TEST FOR BOT"""
import os
from slackclient import SlackClient

BOT_NAME = 'off'

slack_client = SlackClient('xoxb-146341984755-1fYi3Oau3Cx262xcxP3Tzzp0')


if __name__ == "__main__":
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    else:
        print("could not find bot user with the name " + BOT_NAME)