from couchdb.design import ViewDefinition

def get_view_class():
    return ViewDefinition("analysis", "all_fully_ready_both_tiers", \
    '''
function(doc) {
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
        var adict = {};
        var match = /.*-([0-9]*)\.root/;
        for (var i=0;i<temp.length;i++) {
            var tempmatch = match.exec(temp[i].pfn);
            var tempmatch1 = match.exec(temp1[i].pfn);
            if (!tempmatch || !tempmatch1) continue;
            if (!(tempmatch[1] in adict)) adict[tempmatch[1]] = ['', ''];
            if (!(tempmatch1[1] in adict)) adict[tempmatch1[1]] = ['', ''];
            adict[tempmatch[1]][0] = temp[i].pfn;
            adict[tempmatch1[1]][1] = temp1[i].pfn;
        }
        for (var key in adict) {
            emit(doc._id, adict[key]);
        }
     }
    ''')
