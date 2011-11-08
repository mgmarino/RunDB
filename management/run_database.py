import couchdb
import couchdb.mapping as schema
from datetime import datetime
from dateutil import tz
import ROOT
import glob
import re
import cPickle as pickle
import types
from RunDB.utilities import utilities
import os
import sys
from RunDB.management import ServerSingleton, CurrentDBSingleton
from RunDB.views import view_database_updated_docs
from calendar import timegm
from time import strptime
from couchdb_extensions import MappingField

local_server = True
#local_server = False

def RunServer():
    return ServerSingleton.get_server()

def get_current_db_module():
    return CurrentDBSingleton.get_current_db_module()

majorana_db_server = '127.0.0.1:5984'
if local_server:  
    majorana_db_username = ''
    majorana_db_password = ''
else:
    majorana_db_username = 'ewi'
    majorana_db_password = 'darkma11er'

"""
    Following are a set of fields set up primarily 
    for the run database.  They encapsulate a 
    certain type of data
"""

class QADataClass(schema.DictField):
    """
      Quality assurance class, allowing flags to be set based
      upon whether or not QA has been run.
    """
    def __init__(self):
        schema.DictField.__init__(self, schema.Mapping.build(
          qa_check_process_has_been_run = schema.BooleanField(),
          qa_accept_run = schema.BooleanField()))

class DataFileClass(schema.DictField):
    """
      Base class for all data files:
        lfn: logical file name, where the file exists in relation
          to a relative base
        pfn: physical file name, where the file exists.
        md5hash: a hash calculated to protect against file
          corruption
        last_mod_time: last modification time of the file.
    """
    def __init__(self):
        schema.DictField.__init__(self, schema.Mapping.build(
          pfn = schema.TextField(),
          lfn = schema.TextField(),
          md5hash = schema.TextField(),
          last_mod_time = MGDateTimeFieldClass()  ))

class AllReducedDataFilesClass(schema.DictField):
    """
      Encapsulate reduced data file classes.  This class is 
      depracated.  Instead use MappingField in couchdb_extensions.
    """

    def __init__(self):
        schema.DictField.__init__(self, schema.Mapping.build(
          pulser = DataFileClass(),
          low_energy = DataFileClass(),
          high_energy = DataFileClass() ))

class MGPickleFieldClass(schema.Field):
    """
      Mapping for pickled fields, allowing trivial storage of python
      objects within the database.
    """
    def _to_python(self, value):
        # Be smart, try to return a function if includes 'def' 
        temp = pickle.loads(str(value))
        if type(temp) is types.StringType: 
            match_it = re.search('def .*', temp, re.DOTALL) 
            if match_it:
                try:
                    code_obj = compile(temp, '<string>', 'exec') 
                    return types.FunctionType(code_obj.co_consts[0], globals())
                except (SyntaxError,TypeError): 
                    pass
        return temp

    def _to_json(self, value):
        return unicode(pickle.dumps(value,0))

class MGDateTimeFieldClass(schema.DateTimeField):
    """
    Assumes that we obtain a datetime object
    Encapsulates a datatime object (i.e. one created using 
    datetime module to create)
    """   
    def _to_json(self, value):
        # Convert to UTC
        if value.tzinfo:
            value = value.astimezone(tz.tzutc()).replace(tzinfo=None)
        return schema.DateTimeField._to_json(self, value)
    def _to_python_localtime(self, value):
        if isinstance(value, basestring):
            try:
                value = value.split('.', 1)[0] # strip out microseconds
                value = value.rstrip('Z') # remove timezone separator
                timestamp = timegm(strptime(value, '%Y-%m-%dT%H:%M:%S'))
                value = datetime.utcfromtimestamp(timestamp)
            except ValueError, e:
                raise ValueError('Invalid ISO date/time %r' % value)
        return value
       

class MGDocumentClass(schema.Document):
    """ 
      Base class of all documents in the run database
      Includes utility function:

        update_schema 

      Use this to update a document held in the database to a new
      schema.  In other words, if the defined schema changes in the 
      code and the respective object in the database needs to 
      be updated, call the following like:

      >>> server = couchdb.Server('http://localhost:5984/'
      >>> db = server['list-tests']

      >>> class TestDoc(MGDocument):
      ...    title = schema.TextField()

      >>> class TestDocAlt(MGDocument):
      ...    title = schema.TextField()
      ...        test_list = schema.ListField(schema.TextField())

      >>> t1 = TestDoc()
      >>> t1.title = 'Test'
      >>> t1.store(db)

      >>> t2 = TestDocAlt.load(db, t1.id)
      >>> t2 = TestDocAlt.update_schema(t2)
      >>> t2.store(db) # persist back to db

    """ 

    @classmethod
    def update_schema(cls, old_doc):
        """
        Run this on an old document to generate the correct 
        schema and update to the correct rev and ids.
        """
        new_doc = cls()
        def update_field(field, old_field):
            try:
                for sub_field in field:
                    if sub_field in old_field:
                        try:
                            update_field(field[sub_field], old_field[sub_field])
                        except TypeError:
                            #print sub_field, type(sub_field)
                            field[sub_field] = old_field[sub_field]
            except TypeError: 
                # this field is non-iterable, return to the calling function 
                raise

        update_field(new_doc, old_doc)
        #for field in new_doc:
        #    if field in old_doc:
        #        new_doc[field] = old_doc[field]

        if '_rev' in old_doc:
            new_doc['_rev'] = old_doc['_rev']
        new_doc._set_id(old_doc._get_id())
        return new_doc

class PickleDocumentClass(MGDocumentClass):
    """
      Document class for a single pickle field, depracated.
    """
    pickle = MGPickleFieldClass() 

class UpdateDatabaseDocumentClass(MGDocumentClass):
    """
      Class saving when the database has been updated.
      This is useful to save information for external
      daemons so that they know when the last
      update has been run.  FixME, use changes feed of
      couchdb instead of this.
    """
    time_of_last_update = MGDateTimeFieldClass() 

class RunServerClass(couchdb.client.Server):
    
    """
      Workhorse class of the entire RunDB python package,
      this class encapsulates a database object.
      Generally, classes will derive from this class to instantiate
      their own database.

    """
    def __init__(self, db_name, run_doc_class):
        full_url = "http://" + majorana_db_server 
        if majorana_db_username != '' and majorana_db_password != '':
            full_url = ("http://%s:%s@" % (majorana_db_username, majorana_db_password)) + majorana_db_server 
        couchdb.client.Server.__init__(self, full_url)
        if db_name not in self:
            self.run_db = self.create(db_name)
            print "Database created."
        else:
            self.run_db = self[db_name]

        self.run_doc_class = run_doc_class
        
    def get_lfn_path(self):   
        return os.path.expanduser("~/Dropbox/RunData")

    def get_last_update_run(self):
        """
          Returns the last time the database was updated.
          Ret: datetime.datetime object
          Useful for caching when polling daemons last ran. 
        """
        view = view_database_updated_docs.get_view_class()
        all_docs = view(self.get_database()) 
        if not all_docs or len(all_docs) == 0:
            self.set_last_update_run(datetime.fromtimestamp(0))
            return self.get_last_update_run()
        for id in all_docs:
            doc = UpdateDatabaseDocumentClass.load(self.get_database(), 
                                                   str(id.id)) 
            return doc.time_of_last_update
        return 0

    def set_last_update_run(self, time):
        """
          Sets the time the database was updated.
          time: datetime.datetime object
          Useful for caching when polling daemons last ran. 
        """
        view = view_database_updated_docs.get_view_class()
        all_docs = view(self.get_database()) 
        update_doc = None
        if not all_docs or len(all_docs) == 0:
            update_doc = UpdateDatabaseDocumentClass()
            update_doc._set_id("update_doc")
        else:
            for id in all_docs:
                update_doc = UpdateDatabaseDocumentClass.load(
                             self.get_database(), str(id.id)) 
                break
        update_doc.time_of_last_update = time
        update_doc.store(self.get_database())


    def get_database(self):
        """
          Returns db primitive
        """
        return self.run_db

    def run_is_in_database(self, run_number):
        try:
            int_run_number = int(run_number)
        except ValueError:
            return False
        return (str(run_number) in self.get_database())

    def get_doc(self, doc):
        return self.get_run(doc)

    def get_run(self, run_number):
        if self.run_is_in_database(run_number): 
            return self.run_doc_class.load(self.get_database(), str(run_number))
        return None

    def delete_run(self, run_number):
        if self.run_is_in_database(run_number): 
            self.get_database().__delitem__(str(run_number))
            
    def insert_rundoc(self, rundoc):
        if rundoc:
            rundoc.store(self.get_database())
    
    def check_and_update_run(self, run_number):
        """
          Checks to see if a run exists, and updates it if the modification time
          of the local files is more recent than the modification time of the 
          database document.  Deprecated, uses views and update database now. 
        """
        run_doc = self.get_run(run_number)
        if not run_doc:
            run_doc = self.run_doc_class.build_document(run_number)
            if run_doc:
                print "Run %i is not in database, inserting..." % int(run_number)
                self.insert_rundoc(run_doc)


