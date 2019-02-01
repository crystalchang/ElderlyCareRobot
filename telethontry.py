from telethon import TelegramClient, sync, events
from os import system
from gtts import gTTS as gtts
from pygame import mixer

#################### INITIALISE  ###################
api_id = 524136
api_hash = '84360980c78595ec5fa48af726f8917c'
client = TelegramClient('elcie_client', api_id, api_hash)

mixer.init()

#####################################################

# {'123456': {'name': 'crystal', 'relationship':'daughter',
#       'username':'crystalchang'}
# }
# {'daughter':'123456', 'son':'234567',...}
# {'crystal':'123456', 'adam':'234567',...}
addr_book = {}
last_messages = []
last_msg = -1

def add_to_recent(msg_id):
    print("adding to recent")
    print(msg_id)
    last_msg += 1
    if(last_msg == 10):
        last_msg = 0
    print(msg_id)
    last_messages[last_msg] = msg_id
    print(last_messages)
        

def say(stringToRead):
    #stringToRead = stringToRead.replace("''", "")
    tts = gtts(text=repr(stringToRead), lang="en")
    tts.save("tts.mp3")
    mixer.music.load("tts.mp3")
    mixer.music.play()

async def send_to(person, msg):
    try:
        chat = addr_book[person]
        await client.send_message(int(chat),msg)
    except:
        print(person + ' is not in your address book')

# adding relationships using messages
@client.on(events.NewMessage)
async def add_rs_to_addr_book(event):
    msg = str(event.raw_text).lower()
    if ('add relationship' in msg):
        chat = await event.get_chat()
        print('adding relationship')
        segment = msg.split("add relationship ")
        relation = (str(segment[1]))
        addr_book[relation] = chat.id
        print(addr_book)
        await client.send_message(chat,"Got it, " + relation + " has been added!")
        # add chat.name into addr_book

@client.on(events.NewMessage)
async def add_group_to_addr_book(event):
    msg = str(event.raw_text).lower()
    if 'add group' in msg:
        chat = await event.get_chat()
        print('adding group')
        segment = msg.split("add group ")
        relation = (str(segment[1]))
        addr_book[relation] = chat.id
        await client.send_message(chat,"Okay, group " + relation + " has been added!")
        print(addr_book)

# sending message to rs
@client.on(events.NewMessage)
async def send_to_relation(event):
    msg = event.raw_text
    # use voice command
    if 'send to' in msg:
        print('sending')
        segment = msg.split("send to ")
        relation = (str(segment[1]))
        await send_to(relation, 'have you received')

# reading new messages
@client.on(events.NewMessage)
async def read_message(event):
    sender = await event.get_sender()
   # if (sender.id == 67617730):
   #     return
    
    chat = await event.get_chat()
    stringToRead = ""
    stringToRead += "new message from " + str(sender.first_name)
    # from a group chat
    if (chat.id != sender.id):
        stringToRead += " from chat group " + str(chat.title)
    stringToRead += event.raw_text
    say(stringToRead)
    print("new message received")
    last_messages.append(event.message)
    print(last_messages[-1])
    

@client.on(events.NewMessage)
async def repeat_message(event):
    #replace with voice
    msg = str(event.raw_text).lower()
    if "repeat message" in msg:
        print("repeating message")
        # change to -1 when using voice
        print(repr(last_messages[-2].message))


# TODO Repeat message, search message
# TODO Read only messages from other people
if __name__ == "__main__":
    with client:
      client.start()
      client.send_message(67617730,'trying chatid')
      # requires sign in using phone number
      client.run_until_disconnected()
