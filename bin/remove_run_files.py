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
    
    cull = 'all'
    if len(sys.argv) > 2 and sys.argv[2] in avail_second:
        cull = sys.argv[2]
    server = RunServer()
    run = server.get_run(sys.argv[1]) 
    if run:
        if cull == 'tier1' or cull == 'all': 
            for afile in run.root_data_file_tier_1:
                afile.download = False
        if cull == 'tier2' or cull == 'all': 
            for afile in run.output_data_file_tier_2:
                afile.download = False

        server.insert_rundoc(run)
    wake_up()
