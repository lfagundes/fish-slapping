#!/usr/bin/env python
# coding: utf-8

from fish_slapping import Bot
from subprocess import Popen, PIPE

def uptime():
    uptime = Popen('uptime', stdout=PIPE).stdout.read()
    load = float(uptime.split(':')[-1].split(',')[0].strip())

    if load > 4:
        return 'away', uptime
    if load > 2:
        return 'dnd', uptime
    return '', uptime
    
bot = Bot("user@domain.com", "secret_password")
bot.status = uptime
bot.run()
