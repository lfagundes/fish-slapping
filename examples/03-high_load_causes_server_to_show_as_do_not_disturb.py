#!/usr/bin/env python
# coding: utf-8

from fish_slapping import Bot
from subprocess import Popen, PIPE

def uptime():
    # This gets the output of the "uptime" system command
    uptime = Popen('uptime', stdout=PIPE).stdout.read()

    # This parses the uptime to get just the instant load
    load = float(uptime.split(':')[-1].split(',')[0].strip())

    if load > 4:
        return 'dnd', uptime
    if load > 2:
        return 'away', uptime
    return '', uptime
    
bot = Bot("user@domain.com", "secret_password")
bot.status = uptime
bot.run()
