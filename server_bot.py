# -*- coding: utf-8 -*-

# Copyright (c) 2011, Luis Henrique Cassis Fagundes <lhfagundes@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import xmpp, time, os, subprocess, datetime, logging

PRESENCE_HEARTBEAT = 60
ERROR_TIMEOUT = 3600
LOG_PATH = '/var/log/jabber_server_bot.log'
LOG_NAME = 'jabber-bot'

class Finish(Exception):
    pass

class Status(object):
    def __init__(self, msg, tstamp = None, show = ''):
        if tstamp is None:
            tstamp = datetime.datetime.now()
        self.message = msg
        self.tstamp = tstamp
        self.show = show

    @property
    def time(self):
        return self.tstamp.strftime("%Y-%m-%d %H:%M:%S")

class Error(Status):
    def __init__(self, msg, tstamp = None):
        super(Error, self).__init__(msg, tstamp, 'dnd')
        
    @property
    def expired(self):
        return (datetime.datetime.now() - self.tstamp).seconds > ERROR_TIMEOUT


class Log(object):

    def __init__(self, logfile, name=None):
        if name is None:
            self.name = os.path.basename(logfile).split('.')[0]
        else:
            self.name = name
        self.buffer = ''
        self.log = None

        self.logfile = logfile
        self.openfile(start=True)
        self.status = None
        self._error = None
        self.rewind(dtime=ERROR_TIMEOUT)
        self.flush()


    @property
    def real_size(self):
        if os.path.exists(self.logfile):
            return os.path.getsize(self.logfile)
        return 0

    @property
    def pointer(self):
        try:
            return self.log.tell()
        except AttributeError:
            return 0

    def openfile(self, start = False):
        try:
            self.log.close()
        except AttributeError:
            pass

        if not os.path.exists(self.logfile):
            self.log = None
            return
            
        try:
            self.log = open(self.logfile)
            self.ctime = os.path.getctime(self.logfile)
            if start:
                self.log.seek(self.real_size)
        except OSError:
            raise Exception("Log inexistente")
        
    def _char_at(self, pos):
        self.log.seek(pos)
        return self.log.read(1)

    def _rewind_one_line(self):
        pos = self.pointer - 2
        
        while pos > 0 and self._char_at(pos) != '\n':
            pos -= 1

        if pos > 0:
            pos += 1
            
        self.log.seek(pos)
        
    def rewind(self, lines = None, dtime = None):

        if dtime:
            timelimit = datetime.datetime.now() - datetime.timedelta(0, dtime)
            tstamp = datetime.datetime.now()
        
        size = self.real_size
        if size == 0:
            return

        self.log.seek(size)
        
        if lines is None and dtime is None:
            return

        i = 0
        non_log_lines = [0]
        while self.pointer > 0 and (lines is None or i < lines) and (dtime is None or tstamp > timelimit):
            self._rewind_one_line()
            position = self.pointer
            line = self.log.readline()
            self.log.seek(position)
            try:
                tstamp = self.parse_line(line)[0]
            except ValueError:
                # This might be a multi-lined log entry
                # We must not advance counter and time and keep rewinding
                # It's important to count this lines, so that we can advance it in future
                non_log_lines[-1] += 1
                continue
            non_log_lines.append(0)
            i += 1

        if self.pointer > 0 and dtime:
            self.log.readline()
            if len(non_log_lines) > 1:
                for i in range(0, non_log_lines[-2]):
                    self.log.readline()

    @property
    def error(self):
        if self._error is None:
            return None
        if self._error.expired:
            self._error = None        
            return None
        return self._error

    def flush(self):
        if not self.log or self.pointer > self.real_size:
            self.openfile()

        new_bytes = self.real_size - self.pointer

        if not new_bytes:
            return ''
        
        self.buffer += self.log.read(new_bytes)
        message, br, buf = self.buffer.rpartition('\n')
        self.buffer = buf

        lines = message.strip()

        if not lines:
            return ''

        lines = lines.split('\n')
        
        for line in lines:
            if line.isspace():
                continue
            try:
                tstamp, msgtype, msg = self.parse_line(line)
            except ValueError:
                # TODO: unify
                # This might be a multi-lined log entry
                continue
            if msgtype == 'ERROR':
                self._error = Error(msg, tstamp)
            elif msgtype == 'INFO':
                self.status = Status(msg, tstamp)

        return message

    def parse_line(self, line):
        dtime, name, msgtype, msg = line.split(' - ')
        tstamp = datetime.datetime.strptime(dtime.split(',')[0], '%Y-%m-%d %H:%M:%S')
        return tstamp, msgtype, msg

class StreamSession():
    def __init__(self, jid, timeout = None, condition = None):
        self.jid = jid
        self.timeout = timeout
        self.condition = condition
        self.start = datetime.datetime.now()

    @property
    def expired(self):
        if self.timeout and (datetime.datetime.now() - self.start).seconds > self.timeout:
            return True
        if self.condition is not None and not self.condition():
            return True
        return False

class StreamSessionManager(object):

    def __init__(self):
        self.sessions = []

    def add(self, jid, timeout = None, condition = None):
        self.sessions.append(StreamSession(jid, timeout, condition))

    @property
    def receivers(self):
        jids = []
        for jid in [ session.jid for session in self.sessions ]:
            if jid not in jids:
                jids.append(jid)
        return jids
        

    def expire(self):
        jids = []
        i = 0
        while i < len(self.sessions):
            if self.sessions[i].expired:
                jids.append(self.sessions.pop(i).jid)
            else:
                i += 1
        for jid in [ session.jid for session in self.sessions ]:
            try:
                jids.remove(jid)
            except ValueError:
                pass
        return jids

    def remove(self, jid):
        i = 0
        while i < len(self.sessions):
            if self.sessions[i].jid == jid:
                self.sessions.pop(i)
            else:
                i += 1

class JabberStatus(object):
    def __init__(self, show = None, status = None):
        self.show = show
        self.stauts = status
        
class Bot(object):

    LOGS = (Log(LOG_PATH), )

    def __init__(self, jid, password):
        self.logger = self._get_logger()
        self.logs = {}
        self.sessions = {}

        self.jid = jid
        self.password = password
        
        for log in self.LOGS:
            self.add_log(log)

        self.current_status = Status('')
        self.status_msg = ''
        self.status_show = ''

        self.last_presence = None
        self.last_presence_msg = ''

        self.logger.info("Started, connecting...")

        self.connected = False
        
        self.cleared = None


    def add_log(self, log):
        self.logs[log.name] = log
        self.sessions[log.name] = StreamSessionManager()

    def _get_logger():
        logfile = open(LOG_PATH, 'a')
        logger = logging.getLogger(LOG_NAME)
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler(logfile)
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

    def finish(self):
        time.sleep(60) #avoids fast reconnection
        raise Finish

    @property
    def host(self):
        return self.jid.split("@")[1]
    
    @property
    def username(self):
        return self.jid.split("@")[0]


    def connect(self):
        self.client =  xmpp.Client(self.host)
        result = self.client.connect()

        if result:
            self.logger.info("Connected as %s" % result)
        else:
            self.logger.warn("Couldn't connect")
            self.finish()

        auth = self.client.auth(self.username, self.password)

        if auth:
            self.logger.info("Authenticated")
        else:
            self.logger.warn("Couldn't authenticate")
            self.finish()

        self.connected = True

        self.client.RegisterHandler('message', self.message_callback)
        self.client.RegisterDisconnectHandler(self.reconnect)

        self.roster = self.client.getRoster()
        for peer in self.roster.keys():
            self.roster.Authorize(peer)
        self.client.sendInitPresence()

    def reconnect(self):
        self.connected = False
        time.sleep(10)
        self.connect()

    def run(self):
        while True:
            self.cycle()

    def cycle(self):
        try:
            if self.connected:
                self.client.Process(1)
            else:
                self.reconnect()
            self.flush_logs()
            self.set_state()
            self.presence()
        except Exception, e:
            if type(e) is Finish:
                return
            self.logger.error(e)
            time.sleep(5)

    def public_ip(self):
        if not self.public_ip_address or time.time() - self.public_ip_check > 300:
            resp = urllib2.urlopen('http://automation.whatismyip.com/n09230945.asp')
            self.public_ip_address = resp.read()
            self.public_ip_check = time.time()
        return self.public_ip_address

    def presence(self):
        if (self.status_msg == self.last_presence_msg and 
            self.last_presence is not None and
            (datetime.datetime.now() - self.last_presence).seconds < PRESENCE_HEARTBEAT):

            return

        self.client.send(xmpp.Presence(show = self.status_show,
                                       status = self.status_msg)
                         )
                                                                         
        self.last_presence = datetime.datetime.now()
        self.last_presence_msg = self.status_msg

    def flush_logs(self):
        for logname, log in self.logs.items():
            message = log.flush()
            session = self.sessions[logname]

            if message:
                for jid in session.receivers:
                    self.client.send(xmpp.Message(jid, '\n' + message))

            expired = session.expire()
            for jid in expired:
                self.client.send(xmpp.Message(jid, '--- fim de %s' % logname))

    def clear(self):
        self.cleared = datetime.datetime.now()

    def set_state(self):
        status = Status(msg = self.status.get_status(),
                        show = self.status.get_status_show())

        if status.message != self.current_status.message:
            self.current_status = status

        if status.show != self.status_show:
            self.current_status.show = status.show
        
        self.status_show = self.current_status.show
        self.status_msg = '%s %s' % (self.current_status.time,
                                     self.current_status.message)
        
        tstamp = None
        for name, log in self.logs.items():
            if log.error:
                if self.cleared and log.error.tstamp < self.cleared:
                    continue
                if not tstamp or log.error.tstamp > tstamp:
                    tstamp = log.error.tstamp
                    self.status_msg = '%s %s: %s' % (log.error.time,
                                                     name,
                                                     log.error.message)
                    self.status_show = 'dnd'


    def message_callback(self, dispatcher, event):
        sender = event.getFrom()
        sender_id = '%s@%s' % (sender.node, sender.domain)
        message = event.getBody()

        if message is None:
            return

        self.logger.info("Received from %s: %s" % (sender_id, message))

        message = message.split()
        
        if message[0] == 'show':
            target = message[1]
            if len(message) > 2:
                lines = int(message[2])
            else:
                lines = 5

            if not self.logs.get(target):
                self.client.send(xmpp.Message(sender_id, "Target %s unknown" % target))
                self.logger.warn("Target %s unknown" % target)
            else:
                self.sessions[target].add(sender_id)
                self.logs[target].rewind(lines=lines)

        elif message[0] == 'stop':
            for session in self.sessions.values():
                session.remove(sender_id)
            self.client.send(xmpp.Message(sender_id, '--- fim dos logs'))

        elif message[0] == 'uptime':
            message = subprocess.Popen(['uptime'], stdout=subprocess.PIPE).stdout.read()
            self.client.send(xmpp.Message(sender_id, '\n' + message))
            
        elif message[0] == 'ip':
            self.client.send(xmpp.Message(sender_id, self.public_ip()))

        elif message[0] == 'clear':
            self.clear()
            self.presence()
            
        elif message[0] == 'help':
            self.client.send(xmpp.Message(sender_id, HELP))
        else:
            self.logger.warn("Unknown message")

if __name__ == '__main__':
    Bot().run()
