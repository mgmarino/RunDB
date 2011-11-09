#!/bin/env python
import subprocess
from ..views import view_virgin_docs

slac_server = "slac"

def update_rundoc(rundoc):
    """
    Returns whether or not the rundoc has been updated.
    This list is composed with tuples of the following:
       file_dict,
       program_to_make_next_file
       dest_file
    """
    rundoc_was_modified = False
    list_to_check = [ ( rundoc.raw_data_file_tier_0,
                        "~exodata/datacat/prod/datacat find --group binary /EXO/Data/Raw --filter 'nRun==%i'" ),
                      ( rundoc.root_data_file_tier_1, 
                        "~exodata/datacat/prod/datacat find --group root /EXO/Data/Raw --filter 'nRun==%i'" ),
                      ( rundoc.output_data_file_tier_2,
                        "~exodata/datacat/prod/datacat find --group recon /EXO/Data/Processed/ateam --filter 'nRun==%i'" ),
                    ]

    FNULL = None#open("/dev/null",'w')
    for alist, query in list_to_check:
        if query: 
            print "Running: ssh %s %s " % (slac_server, query % int(rundoc.id))
            p2 = subprocess.Popen(["ssh", slac_server, query % int(rundoc.id) ], 
              stdout=subprocess.PIPE) 
            output =  p2.communicate()[0]
            thelist = output.split('\n')
            for afile in thelist:
                if afile == "": continue
                doc = {}
                doc['server_pfn'] = "%s:%s" % (slac_server, afile)
                doc['download'] = True 
                alist.append(doc)
            rundoc_was_modified = True

    return (rundoc, rundoc_was_modified)

def get_view():
    return view_virgin_docs.get_view_class()
