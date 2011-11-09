#!/usr/bin/env python
# coding: utf-8

from subprocess import Popen, PIPE
from fish_slapping import Bot

def hello(sender, message):
    return "Hello to you to, %s" % sender

def who(sender, message):
    return Popen('who', stdout=PIPE).stdout.read()

bot = Bot("user@domain.com", "secret_password")
bot.commands['hello'] = hello
bot.commands['who'] = who
bot.run()
