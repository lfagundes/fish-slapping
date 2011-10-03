#!/usr/bin/env python
# coding: utf-8

import subprocess
from server_bot import Bot, Log
from datetime import datetime

class ApacheLog(Log):
    def parse_line(self, line):

        if self.name == "access":
            msgtype = "INFO"
            tstamp = datetime.strptime(line.split()[3].lstrip('['),
                    "%d/%b/%Y:%H:%M:%S")
            msg = line.split("]")[1]
        else:
            msgtype = "ERROR"
            tstamp = datetime.strptime(line.split(']')[0].lstrip('[') ,
                    "%a %b %d %H:%M:%S %Y")
            msg = line.split("]")[3]

        return tstamp, msgtype, msg  

class Uptime(object):
    def get_status(self):
        return subprocess.Popen("uptime", stdout=subprocess.PIPE).stdout.read()

if __name__ == "__main__":
    Bot.LOGS = (
            ApacheLog("/var/log/apache2/error.log", "error"),
            ApacheLog("/var/log/apache2/access.log", "access"),
            )
    bot = Bot("user@domain.com", "secret_password")
    bot.status = Uptime()
    bot.run()
