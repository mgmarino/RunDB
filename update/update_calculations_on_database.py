from ..management.run_database import RunServer, get_current_db_module
import pkgutil
from ..utilities.utilities import detectCPUs
import os
import sys
import numpy
import time


def run_update_calc( server_build, alist, update_rundoc):
    """
      server: the method to instantiate a new server.
              This is important since we are running in a different thread.
      alist: list of documents to process
      update_rundoc: passed in method to perform the updating
    """
    server = server_build()
    for id in alist:
        run_doc = server.get_doc(id)
        if not run_doc: 
            print "    Error finding %s" % id.id
            continue
        (run_doc, must_reinsert) = update_rundoc(run_doc)
        if not must_reinsert: 
            # This means that probably a dependency has not been updated,
            # get out and come back to this.
            break

        print "    Updating run number: %s" % run_doc.id
        server.insert_rundoc(run_doc)


def update_calculations_on_database():
    server = RunServer()
    if not server.get_lock():
        print "server locked"
        return
    
    def my_import(name):
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod

    # Which database are we using?
    # Grab all the modules from the update directory
    # in this particular database
    # For example, for bege_jc, grab all modules from bege_jc.update
    module_list = []
    current_db_name = '%s.update' % get_current_db_module()
    update_module = my_import(current_db_name)
    for loader,name,ispkg in pkgutil.iter_modules([update_module.__path__[0]]):
        if ispkg: continue
        load = pkgutil.find_loader('%s.%s' % (current_db_name, name))
        mod = load.load_module("%s.%s" % (current_db_name,name))
        module_list.append(mod)

    # How many cpus can we use at once?
    num_cpus = detectCPUs() 
    print "Performing the following updates: " 
    must_cycle = False
    pid_lock_docs = {}
    def get_run_docs_to_update(module_list, ser):
        list_to_return = {} 
        for amod in module_list: 
            # Get the view to use
            view = amod.get_view()
            # Get the list of docs needing update
            list_of_docs = view(ser.get_database())
            for doc in list_of_docs:  
                if doc.id not in list_to_return: 
                    list_to_return[doc.id] = [amod]
                elif amod not in list_to_return[doc.id]:
                    list_to_return[doc.id].append(amod)
        return list_to_return
   
    process_list = get_run_docs_to_update(module_list, server)
    while len(process_list) != 0:
        for doc, mods in process_list.items(): 
            while len(pid_lock_docs) >= num_cpus:  
                # we have to wait for some to finish 
                pid,_ = os.waitpid(-1, 0)
                if pid in pid_lock_docs:
                    del pid_lock_docs[pid]
            if doc not in pid_lock_docs.values(): 
                pid = os.fork()
                if pid: # parent
                    pid_lock_docs[pid] = doc
                else: # child process
                    del server
                    # The following function calls amod.update_rundoc 
                    # on all the records in alist
                    run_update_calc(RunServer, [doc], mods[0].update_rundoc)
                    sys.exit(0)
        # get a new process list
        # Check if any children have died and collect them
        pid,_ = os.waitpid(-1, os.WNOHANG)
        if pid in pid_lock_docs:
            del pid_lock_docs[pid]
        process_list = get_run_docs_to_update(module_list, server)
        time.sleep(5)

    while len(pid_lock_docs) != 0:
        pid,_ = os.waitpid(-1, 0)
        if pid in pid_lock_docs:
            del pid_lock_docs[pid]

    server.reset_lock()
    server.remove_stale_processing_files()
    if must_cycle:
        print "Some documents were updated, cycling again to resolve all updates"
        update_calculations_on_database()
