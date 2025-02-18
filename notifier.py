import requests, json

bot_token = "TOKEN"
chat_id = 0
configured = False

def retrieve_config():
    """
        Loads the basic configuration for the telegram bot.
    """
    try:
        content = json.loads(open("telegram_config.json").read())
        return content["bot_token"], content["chat_id"]
    except FileNotFoundError:
        print("Config file not found, run 'python notifier.py' to setup bot.")
        return None

def message_user(message:str, notify:bool = False)->None:
    """
        Sends message to chat
        Parameters:
         message(str): The string of the message to be sent
         notify(bool): Whether to notify the user or not, only works for channels
    """
    if not configured:
        print(message)
        return
    try:
        data = {
            "chat_id":str(chat_id),
            "text":message,
            "disable_notification": not notify
        }
        headers = {'Content-Type':'application/json'}
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        res = requests.post(url, json=data, headers=headers)
    except:
        print(f"Message couldn't be sent!\nMessage content: {message}")

def setup_bot():
    """
        Retrieves bot ID and from a message sent retrieves the chat id, saves values in file
    """
    print("Welcome to setup for telegram bot notifier!")
    bot_token = input("Enter the bot token: ")
    input("Send a message to the bot before pressing Enter")
    print("Retrieving messages from bot...")
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    res = requests.get(url)
    message_list = res.json()
    if len(message_list) == 0:
        print("No messages have been sent, exiting...")
        return
    last_message = message_list["result"][-1]
    if input(f"Are you {last_message['message']['from']['first_name']}? (y or leave blank for yes)").lower() in ['y', '']:
        chat_id = last_message["message"]["chat"]["id"]
        print(f"Saving chat id as {chat_id}")
        data = {
            "bot_token":bot_token,
            "chat_id":chat_id
        }
        open("telegram_config.json", "w").write(json.dumps(data))

if __name__ == "__main__":
    setup_bot()
else:
    try:
        bot_token, chat_id = retrieve_config()
        configured = True
    except:
        pass
