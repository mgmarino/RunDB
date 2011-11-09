from couchdb.design import ViewDefinition

def get_view_class():
    return ViewDefinition("proc", "stale_files", \
    '''function(doc) {
       if (doc.processing_file && doc.processing_percentage == "100" ) { 
           emit(doc._id, null); 
       }

    }
    '''
)
