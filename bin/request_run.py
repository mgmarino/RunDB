#!/usr/bin/env python
import RunDB.databases.run_db
from RunDB.management.run_database import RunServer 
import sys
from RunDB.views.insert_views import insert_views
from RunDB.utilities.update_daemon import wake_up 
    
if __name__ == '__main__':
    if len(sys.argv) < 2: 
        print sys.argv
        print "Exit"
        sys.exit(1)
    server = RunServer()
    server.request_add_run(sys.argv[1]) 
    wake_up()
