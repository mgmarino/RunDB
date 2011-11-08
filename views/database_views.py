from RunDB.management.run_database import RunServer 

def insert_view_into_database(view):
    """
    Function inserts a view into the database.
    Type of view should be an couchdb.schema.ViewDefinition 
    """
    
    server = RunServer()
    view.sync(server.get_database())
