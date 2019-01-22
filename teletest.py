from telegram.client import Telegram

def new_message_handler(update):
    print('New message!')

if __name__=='__main__':
    tg = Telegram(
        api_id='524136',
        api_hash='84360980c78595ec5fa48af726f8917c',
        phone='+6587335736',
        database_encryption_key='importantkeyfyp',
	files_directory='/home/pi/ElderlyCareRobot',
    )
    tg.login()

    # if this is the first run, library needs to preload all chats
    # otherwise the message will not be sent
    result = tg.get_chats()
    result.wait()

    tg.add_message_handler(new_message_handler)
    tg.idle()  # blocking waiting for CTRL+C

# result = tg.send_message(
#     chat_id=args.chat_id,
#     text=args.text,
# )
# `tdlib` is asynchronous, so `python-telegram` always returns you an `AsyncResult` object.
# You can receive a result with the `wait` method of this object.
# result.wait()
# print(result.update)
