#!/usr/bin/env python
# coding: utf-8

from fish_slapping import Bot, Log

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
    
bot = Bot("user@domain.com", "secret_password")
bot.logs['apache'] = ApacheLog('/var/log/apache2/access.log')
bot.run()
    
