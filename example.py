#!/usr/bin/env python
# coding: utf-8

import subprocess
from server_bot import Bot, Log

from datetime import datetime
class ApacheLog(Log):
    def parse_line(self, line):
        tstamp = datetime.strptime("2011-10-01 %s" % line.split()[3], 
                                   "%Y-%m-%d %H:%M:%S")
        msg  = line.split("]")[3]
        if self.name == "access":
            msgtype = "INFO"
        else:
            msgtype = "ERROR"
        return tstamp, msgtype, msg  

class Uptime(object):
    def get_status(self):
        return subprocess.Popen("uptime", stdout=subprocess.PIPE).stdout.read()

if __name__ == "__main__":
    Bot.LOGS.append(ApacheLog("/var/log/apache2/zahia-error.log", "error"))
    Bot.LOGS.append(ApacheLog("/var/log/apache2/zahia-access.log", "access"))

    bot = Bot("user@domain.com", "secret_password")
    bot.status = Uptime()
    bot.run()
