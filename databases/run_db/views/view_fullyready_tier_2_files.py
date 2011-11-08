from couchdb.design import ViewDefinition

def get_view_class():
    return ViewDefinition("analysis", "all_fully_ready_tier_2_files", \
    '''function(doc) {
        var temp = doc.output_data_file_tier_2;
        if (temp &&
            temp.length != 0) {
            for (var i=0;i<temp.length;i++) {
                if (!temp[i].pfn) {
                    return;
                }
            }
            for (var i=0;i<temp.length;i++) {
                emit(doc._id, temp[i].pfn);
            }

        }
     }
    ''')
