from slacker import Slacker

with open('data/slack.rah') as token:
    slack = Slacker(token.read().strip())



def broadcast(message):
    # Send a message to #general channel
    slack.chat.post_message('#rahchat', message)

# Upload a file
#slack.files.upload('hello.txt')
