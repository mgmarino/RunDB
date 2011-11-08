from RunDB.management.run_database import DataFileClass, \
     RunServerClass, MGPickleFieldClass, MGDocumentClass 
import couchdb.mapping as schema
from views import view_all_runs
import os
import re
import glob
from datetime import datetime
from RunDB.management.run_database import MGDateTimeFieldClass
import time

run_db_name = 'run_db'
data_file_directories=[ '/exo/scratch2/EXOData/tier0',\
                        '/exo/scratch2/EXOData/tier1',\
                        '/exo/scratch2/EXOData/tier2'] 

class RunDB(RunServerClass):
    def __init__(self):
        RunServerClass.__init__(self, run_db_name, 
                              RunDocumentClass)
    def get_run_docs(self):
        view = view_all_runs.get_view_class()
        return view(self.get_database())

    def get_run(self, run_number):
        temp_list = [id.id for id in self.get_run_docs()]
        if str(run_number) in temp_list: 
            return self.run_doc_class.load(self.get_database(), str(run_number))
        return None

    def get_lfn_path(self):   
        return os.path.expanduser("~/Dropbox/RunData/BeGe")


def update_database():
    #First get all the files together 
    import re
    def get_run_number_from_raw_data_file(datafile_name):
        temp_num = int("20" + datafile_name) 
        return temp_num

    run_db = RunDB()
    start_run_time = datetime.now() 
    last_run_time = run_db.get_last_update_run() 
    print "Starting:", start_run_time
    print "Checking for new docs from last run time:",  last_run_time
    print "Checking normal runs"
    temp = os.listdir(data_file_directories[0])
    temp = [line for line in temp if re.match("[0-9]*\Z", line)]
    temp = [line for line in temp 
             if (datetime.fromtimestamp(os.path.getmtime("%s/%s" % 
                   (data_file_directories[0], line))) >= last_run_time or
                 datetime.fromtimestamp(os.path.getctime("%s/%s" % 
                   (data_file_directories[0], line))) >= last_run_time)]                   
    number_list = []
    for file in temp:
        number_list.append(get_run_number_from_raw_data_file(file))

    number_list.sort()
    for num in number_list:
        run_db.check_and_update_run(num)

    # Now check the other documents to make sure they are updated
    # This is kinda dirty and it shouldn't generally happen.
    view = view_all_runs_modification.get_view_class()
    list = view(run_db.get_database())

    field = MGDateTimeFieldClass()
    number_list = []
    for i in list:
        allfiles = i.value
        for afile, timestamp in allfiles:
            if not afile or not timestamp: continue
            this_mod_time = os.path.getmtime(afile)
            timestamp = time.mktime(field._to_python(timestamp).timetuple())
            if this_mod_time != timestamp:
                print afile, this_mod_time, timestamp
                number_list.append(i.id)
                break
    for num in number_list:
        run_db.delete_run(num)
        run_db.check_and_update_run(num)

    run_db.set_last_update_run(start_run_time)

class RunDocumentClass(MGDocumentClass):
    raw_data_file_tier_0 = DataFileClass() 
    root_data_file_tier_1 = DataFileClass() 
    output_data_file_tier_2 =  DataFileClass()

    @classmethod
    def build_document(cls, run_number):
        return_class = RunDocumentClass()
        return_class._set_id(str(run_number))

        return return_class

