#!/usr/bin/env python
import RunDB.databases.run_db
from RunDB.management.run_database import RunServer 
import sys
from RunDB.views.insert_views import insert_views
from RunDB.utilities.update_daemon import wake_up 
    
if __name__ == '__main__':
    avail_second = [
                    'tier1', 
                    'tier2', 
                     'all'
                   ]
    if len(sys.argv) < 2: 
        print "Usage: %s run_number [%s]" % (sys.argv[0], '|'.join(avail_second)) 
        print "  second is option, defaults to all"
        sys.exit(1)
    
    download = 'all'
    if len(sys.argv) > 2 and sys.argv[2] in avail_second:
        download = sys.argv[2]
    server = RunServer()
    run = server.get_run(sys.argv[1]) 
    if run:
        if download == 'tier1' or download == 'all': 
            for afile in run.root_data_file_tier_1:
                afile.download = True
        if download == 'tier2' or download == 'all': 
            for afile in run.output_data_file_tier_2:
                afile.download = True
        server.insert_rundoc(run)
    else:
        server.request_add_run(sys.argv[1])
    wake_up()
