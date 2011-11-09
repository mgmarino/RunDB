from couchdb.design import ViewDefinition

def get_view_class():
    return ViewDefinition("proc", "deleted_files", \
    '''
    function(doc) {
       if (!doc.root_data_file_tier_1) return;
       var tempVar = [ 
                       doc.root_data_file_tier_1,
                       doc.output_data_file_tier_2,
                       doc.raw_data_file_tier_0
                     ];
       for (var i=0;i<tempVar.length;i++) {
           for (var j=0;j<tempVar[i].length;j++) {
               if (tempVar[i][j].download != null &&
                   !tempVar[i][j].download && 
                   tempVar[i][j].pfn) {
                   emit(doc._id, tempVar[i][j].download);
                   return;
               }
           }
       }
    }
    ''',
)
