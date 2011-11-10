NOTE: This project was renamed from JABBER-SERVER-MONITOR to FISH-SLAPPING. 

Fish-slapping is a tool to monitor servers ussing XMPP. With Fish-slapping you can:

  * See all your servers as contacts in your favorite XMPP client
  * Use contact's status message to monitor something relevant, like server load
  * Contact can change its status to DND or Away to alert you of problems
  * Log files can be monitored for error patterns that should alert you
  * Logs can be inspected through messages from your servers
  * Custom commands for quick inspection of servers can be created

Quickstart
==========

Have a XMPP account
-------------------

First, you need a XMPP account for your server, other for you, and you must already be friends. You can use GTalk, for example, but you might prefer to run your own server. Jabberd2 is a good option, since it allows you to easily create accounts and checks status with queries in your favorite database server.

Following examples assume you use some GTalk account. 

The examples also assume you're using a Linux environment. If you manage to go through this tutorial in another environment, please mail the author and tell about your experience.

Run the bot
-----------

Make a python script with following lines, or type it in a python shell:

    >>> from fish_slapping import Bot
    >>> bot = Bot('user@domain.com', 'secret_password', server='talk.google.com')
    >>> bot.run()

You'll see your bot appear online.

Play with the bot
-----------------

This very basic bot does two things:

  * Show it's own log
  * Show the starting time in status

To see how the bot show it's own log, write the follwing message:

  show fish-slapping

You'll see last lines of the bot's log. By the way, this log is located by default at **/tmp/fish-slapping.log**. This log will be streammed to you as new lines are appended to it. To see this, type any nonsense message and see how it appears in log. To stop the stream, just type:

  stop

The time shown in status is in fact the time of the last status change, but since we didn't configure a routine for the status, we just see the starting time and nothing else.

Checking error logs
-------------------

One feature of Fish-slapping is that any error in a log being monitored will appear as a DND (do not disturb) status message. Since the only log being monitored by default is the bot's itself, you can check this feature with a script like the following one:

    >>> from fish_slapping import Bot
    >>> bot = Bot('user@domain.com', 'wrong_password_here', server='talk.google.com')
    >>> bot.connect()
    >>> bot.password = 'correct_password_now'
    >>> bot.run()

You'll see that the bot will start showing an error in its status. To erase this message, just send a message with:

  clear

Adding new logs
---------------

To add new logs, the procedure is:

    >>> from fish_slapping import Bot, Log
    >>> bot = Bot(...)
    >>> bot.logs['some_log_name'] = Log('/path/to/your/log')
    >>> bot.run()

For this to work, the log must implement be in the format:

  %(asctime)s - %(name)s - %(levelname)s - %(message)s

If you need a different log format, you need to implement a parser function that receives one line and returns a tupple of 3 values:

  * a datetime.datetime object representing the time of that message
  * the msg type, that may be 'INFO', 'WARN', 'ERROR' or 'DEBUG' (although only 'ERROR' is relevant now)
  * the message text

An example of this can be found at examples/04-monitor_log_files.py.

The error status will persist for one hour. This time can be overriden by the "error_timeout" parameter of the Log object.

Setting a custom status
-----------------------

If there are no errors in log, a custom status may be shown. For this, you just need to provide a function that returns the desired status. For example, the following routine will use the output of the "uptime" command as status:

    >>> from subprocess import Popen, PIPE
    >>> def uptime():
    >>>     return '', Popen('uptime', stdout=PIPE).stdout.read()
    >>> bot = Bot(...)
    >>> bot.status = uptime
    >>> bot.run()

The uptime() function returns a tupple of two values. The first one can be '', 'away' or 'dnd' and will set the icon status. The second one is the message shown in status. An example that uses the cpu load to choose the status can be found at 03-high_load_causes_server_to_show_as_do_not_disturb.py

Commands
========

Commands are a quick way to interact with your server by sending messages to it. There are some buitin commands, the full list can be checked with the command:

  help

To implement new commands, just create functions that return the desired output:

    >>> def hello(sender, message):
    >>>     return "Hello, %s" % sender
    >>> bot.commands['hi'] = hello

Now, just write to your bot:

  hi

And it will answer to you. Your function will receive as parameter the sender, formatted as user@server, and an array containing with the words sent by you, ignoring the first word (that is the command name). So, in the example above, message will be an empty array. If you type:

  hi cute bot

message will be ['cute','bot']

