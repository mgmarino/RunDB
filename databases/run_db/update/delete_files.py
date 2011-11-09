from ..views import view_deleted_files
import os

def update_rundoc(rundoc):
    """
    Returns whether or not the rundoc has been updated.
    This list is composed with tuples of the following:
       file_dict,
       program_to_make_next_file
       dest_file
    """
    rundoc_was_modified = False
    tempVar = [ 
                rundoc.root_data_file_tier_1,
                rundoc.output_data_file_tier_2,
                rundoc.raw_data_file_tier_0
              ]

    for list_to_check in tempVar:
        for afile in list_to_check:
            if not afile.download:
                if afile.pfn and os.path.exists(afile.pfn):
                    os.unlink(afile.pfn)
                afile.pfn = None
                rundoc_was_modified = True

    return (rundoc, rundoc_was_modified)

def get_view():
    return view_deleted_files.get_view_class()
