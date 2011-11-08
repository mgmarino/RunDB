from couchdb.design import ViewDefinition

def get_view_class():
    return ViewDefinition("analysis", "all_runs", \
    '''function(doc) {
       var my_string = doc._id
       if (isNaN(parseInt(my_string))) return;
       emit(doc._id, null); 
    }
    ''')
