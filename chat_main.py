from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
import telegram
from constants import TOKEN, ACCESS_TOKEN
from class_vk import VK_class
import time

bot = telegram.Bot(token=TOKEN)

API = VK_class(token=ACCESS_TOKEN)
channelUsername = '' #dest (telegram)
period = 1
group = "" #source (vk)

groupCheck = False
periodCheck = False
postStart = False


def start(bot, update):
    global API
    API = VK_class(token=ACCESS_TOKEN)
    update.message.reply_text("The bot is run, "
                              "you can use commands now")


def set_group_(bot, update):
    global groupCheck
    groupCheck = True
    update.message.reply_text("Send the URL of the group.")


def message_checker(bot, update):
    global period, group, periodCheck, groupCheck

    if groupCheck:
        group = update.message.text
        groupCheck = False
        print("Group is " + group)

    elif periodCheck:
        period = int(update.message.text)
        periodCheck = False
        print("Period is " + str(period))


def set_period(bot, update):
    global periodCheck
    periodCheck = True
    update.message.reply_text("Send the period of posts in seconds.")


def start_posting(bot):
    global API, postStart
    postStart = True
    offset = 3
    print("Posting has been started")
    
    while postStart:
        post = API.get_post(offset, 1, domain=group)
        offset += 1
        bot.sendPhoto(chat_id=channelUsername,
                      photo=post[1], caption=post[0])
        print(post)
        time.sleep(period)


def stop_posting(bot, update):
    global postStart
    postStart = False
    print("Posting is stopped")


def help(bot, update):
    update.message.reply_text("This bot reposts from a chosen group. If your group is \'https://vk.com/hatsunism\',"
                              "enter \'hatsunism\' after set group command.")


def main():

    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    ver_handler = CommandHandler('set_group', set_group_)
    dispatcher.add_handler(ver_handler)

    dispatcher.add_handler(CommandHandler('start_posting', start_posting))
    dispatcher.add_handler(CommandHandler('set_period', set_period))
    dispatcher.add_handler(CommandHandler('stop_posting', stop_posting))

    #start(bot, update)
    start_posting(bot)

    help_handler = CommandHandler('help', help)
    dispatcher.add_handler(help_handler)

    message_handler = MessageHandler(Filters.text, message_checker)
    dispatcher.add_handler(message_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

"""
list of commands:
start - Start using the bot
help - Help command
set_group - Type the group url 
set_period - Set the period in seconds
start_posting - Start
stop_posting - Stop
"""
