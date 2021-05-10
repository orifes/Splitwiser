# todo :
#  set up the bot and create config file
#  create batch file to run the task
#  create scheduled task
#  Set expanses limit
import telebot
import re
import os
import sys
import json


def set_bot(guided=True):
    bot = None
    if guided:
        print("Now let's create the Telegram bot.\n"
              " Please open https://t.me/botfather, and follow the instructions to create new bot.\n"
              "At the end of the process you should get a secret token.\n")
    bot_token = input("Please enter the bot token: ")
    if guided:
        print("Great! now you can start a chat with your bot ,or add it to a group.\n"
              "Send a message to the chat you would like the bot to send you the alerts.")
    identify_chat = input(
        "Do you know what the id of the chat you would like the bot to send you the alerts to? (y\\n)\n")
    if identify_chat == "n":
        while True:
            bot = telebot.TeleBot(bot_token)
            try:
                updates = bot.get_updates()
                chat_id = updates[-1].message.chat.id
                break
            except:
                print("There is a problem with the bot.")
                bot_token = input("Please paste your bot token, \n"
                                  "and make sure you have sent a message to it or added it to a group chat,\n"
                                  "token: ")
    else:
        while True:
            chat_id = input("Please paste the id of the chat: ")
            if chat_id.isdigit():
                chat_id = int(chat_id)
                break
            else:
                print("The id should be a number.")
    validate = input("Do you want me to validate the bot is configured successfully? (y/n)\n") == "y"
    if validate:
        if not bot:
            bot = telebot.TeleBot(bot_token)
        try:
            bot.send_message(chat_id, "Hi there! I'm ready!")
        except:
            print("Something is wrong, please rerun the script to try again")
            exit(-1)
    return bot_token, chat_id


def set_spliwise_api(guided=True):
    if guided:
        print("Let's set your API key for Splitwise. Please go to https://secure.splitwise.com/apps , \n"
              "click \"Register your Application\",and follow along...\n"
              "After you app get confirmed,you'll get an API key\n")
    key = input("Paste your Splitwise API key: ")
    group_id = input("Paste the id of the group you want to me monitored,\n"
                     "you can find it by clicking the group name here https://secure.splitwise.com/#/groups/\n"
                     "in the group page , you can copy the number at the end of the url,\n"
                     " for ex. https://secure.splitwise.com/#/groups/88900 => 8890\n"
                     "group id: ")
    return key,group_id


def set_thresholds():
    while True:
        monthly = input("Write in digits only the monthly expenses threshold you want to be alerted on:\n")
        if monthly.isdigit():
            monthly = int(monthly)
            if monthly > 0:
                break
        else:
            print("Invalid threshold value. Write positive integer only.")
    categories = {}
    while True:
        want_cat_thresh = input("Do you want to add an expenses threshold for specific category?(y/n)\n")
        if want_cat_thresh == "y":
            category = input("Category name (case sensitive): ")
            monthly_cat = input("Write in digits only the monthly expenses threshold fo the category:\n")
            if monthly_cat.isdigit():
                monthly_cat = int(monthly_cat)
                if monthly > 0:
                    categories[category] = monthly_cat

            else:
                print("Invalid input ,try again.")
        else:
            break
    return monthly, categories


def schedule_task():
    want_sc = input("Do you want me to schedule the Splitwiser task for you (only for Windows users)? (y/n)\n")
    if want_sc == "y":
        time_period = input("Great! Do you want Splitwiser to run weekly or daily? (w/d)\n")
        if time_period == "w":
            time_period = "WEEKLY"
        elif time_period == "d":
            time_period = "DAILY"
        else:
            print("Invalid input, please try again.")
            return
        time_pattern = re.compile("\d?\d:\d\d")
        time_input = input("In what time you want the task to run? Enter in \'hh:mm\' format\n")
        if time_pattern.match(time_input):
            print("Thanks, working on it!")
            split_wiser_command = sys.executable + " " + os.path.abspath(os.curdir) + os.sep + "split_wiser.py"
            os.system(
                f"SCHTASKS /CREATE /SC {time_period} /TN \"SplitwiserRunner\" /TR \"{split_wiser_command}\" /ST {time_input}")


CONFIG_FILE = "splitwiser-conf.json"
BOT_TOKEN_KEY, CHAT_ID_KEY = "bot_token", "chat_id"
SPLIT_API_KEY, SPLIT_GROUP_KEY = "split_key", "split_group_key"
THRESHOLD_KEY, CAT_KEY = "threshold", "categories"


def get_config():
    with open(CONFIG_FILE) as f:
        return json.loads(f.read())


def main_install():
    config = {}
    guided = input("Do you want to have detailed instructions? (y/n)\n") == "y"
    config[BOT_TOKEN_KEY], config[CHAT_ID_KEY] = set_bot(guided)
    config[SPLIT_API_KEY],config[SPLIT_GROUP_KEY] = set_spliwise_api(guided)
    config[THRESHOLD_KEY], config[CAT_KEY] = set_thresholds()
    schedule_task()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)


if __name__ == '__main__':
    main_install()
