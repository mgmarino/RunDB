from couchdb.design import ViewDefinition

def get_view_class():
    return ViewDefinition("analysis", "all_virgin_tier_2_files", \
    '''function(doc) {
        if (doc.output_data_file_tier_2 &&
            doc.output_data_file_tier_2.length != 0) {
            for (var i=0;i<doc.output_data_file_tier_2.length;i++) {
                if (!doc.output_data_file_tier_2[i].pfn) {
                    emit(doc._id, null);
                    return;
                }
            }
        }
     }
    ''')
