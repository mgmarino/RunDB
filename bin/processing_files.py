#!/usr/bin/env python
import RunDB.databases.run_db
from RunDB.management.run_database import RunServer
server = RunServer()
alist =  server.get_processing_files()
for afile in alist: print afile.value
