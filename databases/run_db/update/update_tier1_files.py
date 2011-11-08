#!/bin/env python
import subprocess
import os
from ..views import view_virgin_tier_1_files

location = "/exo/scratch2/EXOData"

def download_file(file_loc, run_no):
    full_path = os.path.join(location, str(run_no))
    if not os.path.exists(full_path): 
        os.makedirs(full_path)
    afile_name = os.path.basename(file_loc.split(':')[1])
    print "Running: rsync -avz -P %s %s/ " % (file_loc, full_path)
    p2 = subprocess.Popen(["rsync", "-avz", "-p", file_loc, full_path ], 
      stdout=subprocess.PIPE) 
    output =  p2.communicate()[0]
    return os.path.join(full_path, afile_name)

def update_rundoc(rundoc):
    """
    Returns whether or not the rundoc has been updated.
    This list is composed with tuples of the following:
       file_dict,
       program_to_make_next_file
       dest_file
    """
    rundoc_was_modified = False

    for adoc in rundoc.root_data_file_tier_1:
        file_loc = adoc.server_pfn
        if file_loc: 
            adoc.pfn = download_file(file_loc, rundoc.id) 
            rundoc_was_modified = True

    return (rundoc, rundoc_was_modified)

def get_view():
    return view_virgin_tier_1_files.get_view_class()
