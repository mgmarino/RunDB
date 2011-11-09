#!/usr/bin/env python
import RunDB.databases.run_db
from RunDB.management.run_database import RunServer
server = RunServer()
server.reset_lock()
