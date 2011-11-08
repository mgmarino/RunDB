from ..management.run_database import RunServer, get_current_db_module
import pkgutil
from ..utilities.utilities import detectCPUs
import os
import sys
import numpy


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
    for amod in module_list: 
        # Get the view to use
        view = amod.get_view()
        # Get the list of docs needing update
        list_of_docs = view(server.get_database())
        print "  %s" % amod.__name__

        # Now split up the list for number of cpus
        total_list = numpy.array([id.id for id in list_of_docs])
        if len(total_list) > 0: must_cycle = True

        all_lists = [total_list[i::num_cpus] for i in range(num_cpus)]

        # ship out to different threads
        # We use a fork because the amount of work done
        # by the child should be fairly significant, making
        # the amount of time spent to fork negligible.  
        thread_list = []
        for alist in all_lists: 
            if len(alist) == 0: continue # Don't send out for 0 length lists
            pid = os.fork()
            if pid: # parent
                thread_list.append(pid)
            else: # child process
                del server
                # The following function calls amod.update_rundoc 
                # on all the records in alist
                run_update_calc(RunServer, alist, amod.update_rundoc)
                sys.exit(0)
                # stop here for the child process

        # Wait for worker children to complete
        for thread in thread_list:
            os.waitpid(-1, 0)

    if must_cycle:
        print "Some documents were updated, cycling again to resolve all updates"
        update_calculations_on_database()
