#!/usr/local/bin/python
def update_schema():
    from run_database import RunServer, RunDocumentClass

    server = RunServer()
    
    for id in server.get_database():
        run_doc = server.get_run(id)
        run_doc = RunDocumentClass.update_schema(run_doc)
        print "Updating run number: %s" % run_doc.id
        server.insert_rundoc(run_doc)

if __name__ == '__main__':
    # Means we are called as a script
    update_schema()
