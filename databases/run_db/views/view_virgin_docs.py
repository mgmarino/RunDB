from couchdb.design import ViewDefinition

def get_view_class():
    return ViewDefinition("analysis", "all_virgin_docs", \
    '''function(doc) {
        if ((doc.raw_data_file_tier_0 &&
            doc.raw_data_file_tier_0.length == 0 )||
            (doc.root_data_file_tier_1 &&
            doc.root_data_file_tier_1.length == 0) ||
            (doc.output_data_file_tier_2 &&
            doc.output_data_file_tier_2.length == 0)
            ) {
            emit(doc._id, null);
        }
     }
    ''')
