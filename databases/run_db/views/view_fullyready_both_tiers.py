from couchdb.design import ViewDefinition

def get_view_class():
    return ViewDefinition("analysis", "all_fully_ready_both_tiers", \
    '''function(doc) {
        var temp = doc.output_data_file_tier_2;
        var temp1 = doc.root_data_file_tier_1;
        if (!temp || !temp1 ||
            temp.length == 0 || 
            temp1.length != temp.length) return;
        for (var i=0;i<temp.length;i++) {
            if (!temp[i].pfn || !temp1[i].pfn) {
                return;
            }
        }
        for (var i=0;i<temp.length;i++) {
            emit(doc._id, [temp[i].pfn, temp1[i].pfn]);
        }

        }
     }
    ''')
