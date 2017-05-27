from slacker import Slacker

def config_slack():
    global slack

    with open('data/slack.rah') as token:
        slack = Slacker(token.read().strip())

def broadcast(channel, message):
    slack.chat.post_message(channel, message)
