from slacker import Slacker

#Configures slack with slack token
def config_slack():
    try: #Try except incase connection fails
        global slack

        with open('data/slack.rah') as token:
            slack = Slacker(token.read().strip())
    except:
        pass

#Print message + send to slack
def broadcast(channel, message):
    print(message)
    try:
        slack.chat.post_message(channel, message)
    except:
        pass
