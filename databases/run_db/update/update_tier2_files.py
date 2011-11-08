#!/bin/env python
import subprocess
import os
from ..views import view_virgin_tier_2_files
from update_tier1_files import download_file

location = "/exo/scratch2/EXOData"

def update_rundoc(rundoc):
    """
    Returns whether or not the rundoc has been updated.
    This list is composed with tuples of the following:
       file_dict,
       program_to_make_next_file
       dest_file
    """
    rundoc_was_modified = False

    for adoc in rundoc.output_data_file_tier_2:
        file_loc = adoc.server_pfn
        if file_loc: 
            adoc.pfn = download_file(file_loc, rundoc.id) 
            rundoc_was_modified = True

    return (rundoc, rundoc_was_modified)

def get_view():
    return view_virgin_tier_2_files.get_view_class()
