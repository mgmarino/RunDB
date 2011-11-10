from couchdb.design import ViewDefinition

def get_view_class():
    return ViewDefinition("proc", "processing_files", \
    '''function(doc) {
       if (doc.processing_file) { 
           var tmp = doc.processing_time_left.split(':');
           var minutes = 0;
           if (tmp.length == 3) { 
             minutes = 60*parseInt(tmp[0]) +
                       parseInt(tmp[1]) + 
                       parseInt(tmp[2])/60.;
           }
           emit(doc.processing_file.split("/").pop(), 
             [parseInt(doc.processing_percentage)+0.5, minutes]
              ); 
           return;
       }
       var tempVar = doc.root_data_file_tier_1;
       if (tempVar &&
           tempVar.length != 0) {
           for (var i=0;i<tempVar.length;i++) {
               if (tempVar[i].server_pfn &&
                     !tempVar[i].pfn && tempVar[i].download) {
                   emit(tempVar[i].server_pfn.split("/").pop(), [0,0]);
               }
           }
       }
       tempVar = doc.output_data_file_tier_2;
       if (tempVar &&
           tempVar.length != 0) {
           for (var i=0;i<tempVar.length;i++) {
               if (tempVar[i].server_pfn &&
                     !tempVar[i].pfn && tempVar[i].download) {
                   emit(tempVar[i].server_pfn.split("/").pop(), [0,0]);
               }
           }
       }

    }
    ''',
    '''
    function(keys, values) {
       if (values.length == 0) return 0;
       var sum = values[0]; 
       for (var i=1;i<values.length;i++) {
         for (var j=0;j<values[i].length;j++) {
             sum[j] += values[i][j];
         }
       }
       return sum;
    }
    '''
)
