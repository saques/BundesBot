#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Simple Bot to send timed Telegram messages.
# This program is dedicated to the public domain under the CC0 license.
This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""


from telegram.ext import Updater, CommandHandler
from datetime import datetime
from num2words import num2words
import logging
import os
import requests
from Context import Context
import random
from bs4 import BeautifulSoup

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# +3 hs for NA
def get_seconds(tgt_s):
    current = datetime.now().replace(year=1900, day=1, month=1)
    tgt = datetime.strptime(tgt_s, '%H:%M:%S').replace(year=1900, day=1, month=1)
    if current > tgt:
        tgt = tgt.replace(day=2)
    return (tgt-current).total_seconds()


def get_text():
    r = requests.get("http://www.dw.com/de")
    body = r.text
    soup = BeautifulSoup(body, "html.parser")
    teasers = soup.findAll("div", {"class": "basicTeaser"})
    teaser = teasers[random.randrange(len(teasers))]
    return teaser.text


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Hello! Use /set <time> <interval> <initial_count> to schedule random german texts!')


def alarm(bot, job):
    """Send the alarm message."""

    try:
        text = get_text()
    except:
        text = "NEIN"

    bot.send_message(job.context.chat_id, text="Bundesbitakor Nº %s \n %s" % (num2words(job.context.n, lang='de'), text))
    job.context.n += 1


def set_timer(bot, update, args, job_queue, chat_data):
    """Add a job to the queue."""
    chat_id = update.message.chat_id

    if chat_id in chat_data:
        update.message.reply_text('You already have an active timer. Use /unset to remove.')
        return

    try:
        # args[0] should contain a valid time

        initial = get_seconds(args[0])
        logger.info('Seconds diff "%d"', initial)

        # args[1] should contain a positive integer indicating the interval between messages
        n = int(args[1])
        if n < 0:
            update.message.reply_text('Interval must be positive')
            return

        # Add job to queue
        job = job_queue.run_repeating(alarm, n, first=initial, context=Context(chat_id, int(args[2])))
        chat_data[chat_id] = job

        update.message.reply_text('Timer successfully set!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <time> <interval> <initial_count>')




def unset(bot, update, chat_data):
    """Remove the job if the user changed their mind."""

    chat_id = update.message.chat_id

    if chat_id not in chat_data:
        update.message.reply_text('You have no active timer')
        return

    job = chat_data[chat_id]
    job.schedule_removal()
    del chat_data[chat_id]

    update.message.reply_text('Timer successfully unset!')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Run bot."""

    token = os.environ['TELEGRAM_TOKEN']

    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()