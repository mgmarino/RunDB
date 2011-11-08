import RunDB.views
dirname = RunDB.views.__path__[0]
__path__.insert(0, dirname)
#import pkgutil
#module_dict = globals()
#current_db_name = RunDB.views.__name__
#for loader,name,ispkg in pkgutil.iter_modules([RunDB.views.__path__[0]]):
#    if ispkg: continue
#    load = pkgutil.find_loader('%s.%s' % (current_db_name, name))
#    mod = load.load_module("%s.%s" % (current_db_name,name))
#    module_dict[mod.__name__] = mod
