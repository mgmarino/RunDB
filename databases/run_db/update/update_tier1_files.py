#!/bin/env python
import subprocess
import os
from ..views import view_virgin_tier_1_files
from RunDB.management.run_database import RunServer
import time, re
import tempfile

locations = ["/exo/scratch2/EXOData", "/exo/scratch0/EXOData"]

def download_file(file_loc, run_no):
    location = None 
    for loc in locations:
        if not os.path.exists(loc): 
            os.makedirs(loc)
        if not location: 
            location = loc
            continue
        oldstat = os.statvfs(location)
        newstat = os.statvfs(loc)
        # Choose the one with more space.
        # This could result in things being scattered, but we don't care
        if newstat.f_bavail > oldstat.f_bavail: location = loc
        
    full_path = os.path.join(location, str(run_no))
    if not os.path.exists(full_path): 
        os.makedirs(full_path)
    afile_name = os.path.basename(file_loc.split(':')[1])
    complete_path = os.path.join(full_path, afile_name)
    RunServer().add_processing_file(complete_path)
    out_file, tmp_name = tempfile.mkstemp()
    print "Running: rsync -avz -P %s %s/ " % (file_loc, full_path)
    p2 = subprocess.Popen(["rsync", "-avz", "-P", file_loc, full_path+"/" ], 
      stdout=out_file, stderr=subprocess.STDOUT) 
    temp = p2.poll()
    while temp == None:
        time.sleep(10)
        temp = p2.poll()
        last_line =  open(tmp_name).readlines()
        if len(last_line) == 0: continue
        last_line = last_line[-1]
        match_it = re.match(".* ([0-9]*)%.* ([0-9]*:[0-9]*:[0-9]*).*", last_line)
        if not match_it: continue
        RunServer().update_processing_file(complete_path, match_it.group(1), match_it.group(2))
    os.unlink(tmp_name)
    if temp < 0: return None
    RunServer().update_processing_file(complete_path, "100", "0")
    return complete_path

def update_rundoc(rundoc):
    """
    Returns whether or not the rundoc has been updated.
    This list is composed with tuples of the following:
       file_dict,
       program_to_make_next_file
       dest_file
    """
    rundoc_was_modified = False

    complete_path_list = []
    for adoc in rundoc.root_data_file_tier_1:
        file_loc = adoc.server_pfn
        if file_loc and not adoc.pfn: 
            adoc.pfn = download_file(file_loc, rundoc.id) 
            complete_path_list.append(adoc.pfn)
            rundoc_was_modified = True

    for path in complete_path_list:
        if path == None: continue
        RunServer().remove_processing_file(path)
    return (rundoc, rundoc_was_modified)

def get_view():
    return view_virgin_tier_1_files.get_view_class()
