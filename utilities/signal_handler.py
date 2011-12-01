import threading
"""
  SignalHandler handles signals being sent to and from a process.
"""
class SignalHandler:
    msg_semaphore = threading.Event() 
    msg_die = threading.Event() 
    @classmethod
    def msg_handler(cls, signum, frame):
       # We've received a msg from the user,
       # check the msg semaphore.  
       print "Recieved signal to wake"
       cls.msg_semaphore.set()

    @classmethod
    def exit_handler(cls, signum, frame):
       # We've received a kill msg 
       print "Recieved signal to shutdown"
       cls.msg_die.set()


    @classmethod
    def wait_on_msg(cls):
	# We need to release the block every so often to allow the signal
	# handler to be called
	while (not cls.msg_semaphore.wait(1) 
               and not cls.msg_die.wait(0)): pass
        if (cls.msg_die.wait(0)): return False
        cls.msg_semaphore.clear()
        return True

    

