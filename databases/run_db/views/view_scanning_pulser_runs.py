from couchdb.design import ViewDefinition

def get_view_class():
    return ViewDefinition("final", "all_scanning_pulser_runs", \
    '''
function(doc) {
       if (doc.ln_data_file) return;
       var int_of_doc_id = parseInt(doc._id);
       if (isNaN(int_of_doc_id)) return;

       // We don't accept any runs before 4 December.  
       // The runs before this were with a different DAQ system.
       // i.e. no digitized pulses.
       if (int_of_doc_id < 20091204180000) {
         return;
       }
       // Juan ran a calibration run on the 17th of Dec, from his email:
       //Mike, you'll notice the file today at 12:31 is large. We performed a
       //scanning pulser calibration extending all the way out to the maximum
       //range of ch2 (I had limited measurements to the range of ch1, and want
       //to see how rise times compare with those in the known peaks up there
       //in energy)
       if (int_of_doc_id == 20091217123128 ||
           int_of_doc_id == 20091217123841) {
         emit(parseInt(doc._id), [doc.output_data_file_tier_2.lfn,
                                  doc.root_data_file_tier_1.pfn]); 
       }
     }
    ''')
