import RunDB.databases.run_db
from RunDB.update.update_calculations_on_database import update_calculations_on_database
from RunDB.utilities.daemon import get_pid_file, Daemon
import signal
from RunDB.utilities.signal_handler import SignalHandler
import sys
import os

class CouchUpdateDaemon(Daemon):
    def wake_up(self):
        pid = self.get_pid()
        if not pid:
            self.start()
            pid = self.get_pid()
            if not pid:
                print "Can't start daemon!"
                return
        "Wake the guy up"
        os.kill(pid, signal.SIGUSR1)

    def run(self):
        signal.signal(signal.SIGUSR1, SignalHandler.msg_handler)
        signal.signal(signal.SIGINT, SignalHandler.exit_handler)
        while SignalHandler.wait_on_msg():
            print "Processing"
            update_calculations_on_database()
        print "Exit"

def wake_up():
    daemon = CouchUpdateDaemon(get_pid_file())
    daemon.wake_up()

def update_daemon(command):
    daemon = CouchUpdateDaemon(get_pid_file())
    avail_commands = { 'start'  : daemon.start,
                       'stop'   : daemon.stop, 
                       'forcestop'   : daemon.force_stop, 
                       'restart': daemon.restart, 
                       'check'  : daemon.check, 
                       'wake'  : daemon.wake_up, 
                     }
    if command not in avail_commands.keys():
       output_string = "Usage: script.py "
       for akey in avail_commands.keys():
           output_string += akey + "|"
       output_string = output_string[:-1]
       print output_string
       sys.exit(1)
    
    avail_commands[command]()
