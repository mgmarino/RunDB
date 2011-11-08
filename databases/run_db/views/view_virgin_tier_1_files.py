from couchdb.design import ViewDefinition

def get_view_class():
    return ViewDefinition("analysis", "all_virgin_tier_1_files", \
    '''function(doc) {
        if (doc.root_data_file_tier_1 &&
            doc.root_data_file_tier_1.length != 0) {
            for (var i=0;i<doc.root_data_file_tier_1.length;i++) {
                if (!doc.root_data_file_tier_1[i].pfn) {
                    emit(doc._id, null);
                    return;
                }
            }
        }
     }
    ''')
