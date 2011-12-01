#!/bin/env python
import subprocess
from ..views import view_virgin_docs

slac_server = "slac-single"

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
        already_in_files = [tmp.server_pfn for tmp in alist]
        if query: 
            print "Running: ssh %s %s " % (slac_server, query % int(rundoc.id))
            p2 = subprocess.Popen(["ssh", slac_server, query % int(rundoc.id) ], 
              stdout=subprocess.PIPE) 
            output =  p2.communicate()[0]
            # Check to see if we failed.
            retVal = p2.returncode
            if retVal == None or retVal < 0: 
                print output, retVal 
                continue
            thelist = output.split('\n')
            for afile in thelist:
                if afile == "": continue
                doc = {}
                doc['server_pfn'] = "%s:%s" % (slac_server, afile)
                doc['download'] = True 
                if doc['server_pfn'] in already_in_files: continue
                alist.append(doc)
            if len(alist) == 0:
                doc = {}
                doc['download'] = False 
                alist.append(doc)
            rundoc_was_modified = True

    return (rundoc, rundoc_was_modified)

def get_view():
    return view_virgin_docs.get_view_class()
