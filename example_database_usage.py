import RunDB.databases.run_db
from management.run_database import RunServer

server = RunServer()

# loop over all the accepted runs
for record in server.get_run_docs():
    doc = server.get_run(record.id)
    print "Run number: %s, gretina file: %s" %(doc._get_id(), doc.root_data_file_tier_1.pfn)
