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
    def uptime(self):
        return subprocess.Popen("uptime", stdout=subprocess.PIPE).stdout.read()

    def load(self):
        return float(self.uptime().split(':')[-1].split(',')[0].strip())

    def get_status(self):
        return self.uptime()

    def get_status_show(self):
        load = self.load()
        if load > 4:
            return 'dnd'
        if load > 2:
            return 'away'
        return ''

if __name__ == "__main__":

    bot = Bot("user@domain.com", "secret_password")
    bot.status = Uptime()
    bot.add_log(ApacheLog("/var/log/apache2/error.log", "error"))
    bot.add_log(ApacheLog("/var/log/apache2/access.log", "access"))
    bot.run()
