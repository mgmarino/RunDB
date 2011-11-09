from couchdb.design import ViewDefinition

def get_view_class():
    return ViewDefinition("proc", "processing_files", \
    '''function(doc) {
       if (doc.processing_file) { 
           emit(doc.processing_file.split("/").pop(), parseInt(doc.processing_percentage)+0.5); 
           return;
       }
       var tempVar = doc.root_data_file_tier_1;
       if (tempVar &&
           tempVar.length != 0) {
           for (var i=0;i<tempVar.length;i++) {
               if (tempVar[i].server_pfn &&
                     !tempVar[i].pfn && tempVar[i].download) {
                   emit(tempVar[i].server_pfn.split("/").pop(), 0);
               }
           }
       }
       tempVar = doc.output_data_file_tier_2;
       if (tempVar &&
           tempVar.length != 0) {
           for (var i=0;i<tempVar.length;i++) {
               if (tempVar[i].server_pfn &&
                     !tempVar[i].pfn && tempVar[i].download) {
                   emit(tempVar[i].server_pfn.split("/").pop(), 0);
               }
           }
       }

    }
    ''',
    '''
    function(keys, values) {
       var sum = 0;
       for (var i=0;i<values.length;i++) {
           sum += values[i];
       }
       return sum;
    }
    '''
)
