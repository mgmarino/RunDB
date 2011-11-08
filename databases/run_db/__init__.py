from RunDB.management import ServerSingleton, CurrentDBSingleton
from db import RunDB
ServerSingleton.set_server(RunDB)
CurrentDBSingleton.set_current_db_module(__name__)
