import RunDB.databases.run_db
from RunDB.management.run_database import RunServer 
server = RunServer()
for run in server.get_run_docs():
    arun =  server.get_run(run.key)
    arun.update_schema(arun)
    for doc in arun.output_data_file_tier_2:
        doc.download = True
    for doc in arun.root_data_file_tier_1:
        doc.download = True
    server.insert_rundoc(arun)
    
