#!/usr/bin/env python
# coding: utf-8

from fish_slapping import Bot
from subprocess import Popen, PIPE

def uptime():
    return Popen('uptime', stdout=PIPE).stdout.read()

bot = Bot("user@domain.com", "secret_password")
bot.status = uptime
bot.run()
