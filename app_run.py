from telegram.ext.dispatcher import run_async

import telegram
import logging
import os
import urllib.request
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

import cc2650_manual_read as sensortag
from credentials import bot_token
import picture_click as camera
import json
import random
import platform
import asyncio
import string
import paho.mqtt.client as mqtt
import time

message_check = ""

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected.")
        client.subscribe("Group_99/IMAGE/predict")
    else:
        print("Failed to connect. Error code: %d." % rc)

def on_message(client, userdata, msg):
    global message_check
    print("Received message from server.")
    resp_dict = json.loads(msg.payload)
    message_check = resp_dict
    print(resp_dict)

def setup(hostname):
    print("setting up")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(hostname)
    client.loop_start()
    return client

client = setup("localhost")


def start_info(bot, update):

    user_first_name = update.message.from_user.first_name
    message = "Hi {}, let's start".format(user_first_name)
    print("sent")
    client.publish("Group_99/IMAGE/train", json.dumps(message))
    print("begin timer")
    time.sleep(10)
    print("timer ended")
    global message_check
    update.message.reply_text(message_check)
    print("done")
    #client.publish("Group_99/IMAGE/train", json.dumps(message))

def health_check(bot, update):
    message = str(sensortag.temperature_check())
    print(message)
    update.message.reply_text(message)

def click_image(bot, update):
    camera.click_save_picture(1)
    update.message.reply_text("Succesffuly Done")

def main():
    bs()
    while True:
        pass

def bs():

    #client.publish("Group_99/IMAGE/train", json.dumps("ok"))

    #Start the bot
    # Create an event handler
    updater = Updater('1453184100:AAHFFqX6Rd9TxEloXSIH2QpOKKxTli8k6ZY') #API key

    # Get dispatcher to register handlers
    dp = updater.dispatcher

    # Register different commands
    dp.add_handler(CommandHandler('start', start_info))
    dp.add_handler(CommandHandler('health_check', health_check))
    dp.add_handler(CommandHandler('click_image', click_image))

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__=="__main__":
    main()
