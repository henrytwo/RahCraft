from slacker import Slacker

def config_slack():
    try:
        global slack

        with open('data/slack.rah') as token:
            slack = Slacker(token.read().strip())
    except:
        pass

def broadcast(channel, message):
    print(message)
    try:
        slack.chat.post_message(channel, message)
    except:
        pass
