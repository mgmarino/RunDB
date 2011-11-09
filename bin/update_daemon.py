#!/usr/bin/env python
import RunDB.utilities.update_daemon as ud 
import sys

if __name__ == '__main__':
    if len(sys.argv) != 2: ud.update_daemon("")
    else: ud.update_daemon(sys.argv[1])
