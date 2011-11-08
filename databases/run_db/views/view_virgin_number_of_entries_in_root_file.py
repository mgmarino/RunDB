from couchdb.design import ViewDefinition

def get_view_class():
    return ViewDefinition("analysis", "virgin_number_of_entries_in_root_file", \
    '''function(doc) {
       if ( doc.root_data_file_tier_1 && 
            doc.root_data_file_tier_1.last_mod_time &&
            doc.root_data_file_tier_1.md5hash &&
            !doc.number_of_entries_in_tier1_root_tree) {
         emit(doc._id, null); 
       }
    }
    ''')
