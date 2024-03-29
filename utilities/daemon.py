#!/usr/bin/env python
import signal 
import sys, os, time, atexit
import errno

def get_pid_file():
    return "/exo/scratch0/pid/couchb_update.pid"

def get_log_file():
    return "/exo/scratch0/run_db_log/run_db.log"

class Daemon:
	"""
	A generic daemon class.
	
	Usage: subclass the Daemon class and override the run() method
	"""
	def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
		self.stdin = stdin
		self.stdout = stdout
		self.stderr = stderr
		self.pidfile = pidfile
	
	def daemonize(self):
		"""
		do the UNIX double-fork magic, see Stevens' "Advanced 
		Programming in the UNIX Environment" for details (ISBN 0201563177)
		http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
		"""
		try: 
			pid = os.fork() 
			if pid > 0:
				# exit first parent
				sys.exit(0) 
		except OSError, e: 
			sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1)
	
		# decouple from parent environment
		os.chdir("/") 
		os.setsid() 
		os.umask(0) 
	
		# do second fork
		try: 
			pid = os.fork() 
			if pid > 0:
				# exit from second parent
				sys.exit(0) 
		except OSError, e: 
			sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1) 
	
		# redirect standard file descriptors
		sys.stdout.flush()
		sys.stderr.flush()
		si = file(self.stdin, 'r')
		#so = file(self.stdout, 'a+')
		so = file(get_log_file(), 'a+')
		#se = file(self.stderr, 'a+', 0)
		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(so.fileno(), sys.stderr.fileno())
	
		# write pidfile
		atexit.register(self.delpid)
		pid = str(os.getpid())
		file(self.pidfile,'w+').write("%s\n" % pid)

        def checkpid(self):
            # Check if pid is still running
            pid = self.get_pid()
            if not pid: return False
            return os.path.exists("/proc/%i" % pid)
	
	def delpid(self):
                pid = self.get_pid()
                if not pid: return
		# it's possible that other spawns may occur, only delete this
		# when the main pid exits.
		if pid != str(os.getpid()): return 
		if os.path.exists(self.pidfile): os.remove(self.pidfile)

	def get_pid(self):
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None
		return pid


        def check(self):
                """
                Runs a check
                """
                if self.checkpid():
                     print "Daemon is running"
                else:
                     print "Daemon is not running"
	


	def start(self):
		"""
		Start the daemon
		"""
		# Check for a pidfile to see if the daemon already runs

		if self.get_pid():
			message = "pidfile %s already exist. Daemon already running?\n"
			sys.stderr.write(message % self.pidfile)
                        if not self.checkpid():
			    sys.stderr.write("Daemon not running, deleting pidfile and continue.\n")
		            if os.path.exists(self.pidfile): os.remove(self.pidfile)
			else: sys.exit(1)
		
		# Start the daemon
		self.daemonize()
		self.run()

        def stop(self):
            self.signal_daemon(signal.SIGINT)

        def force_stop(self):
            self.signal_daemon(signal.SIGKILL)

	def signal_daemon(self, withsignal):
		"""
		Stop the daemon
		"""
		# Get the pid from the pidfile
                pid = self.get_pid()

		if not pid:
			message = "pidfile %s does not exist. Daemon not running?\n"
			sys.stderr.write(message % self.pidfile)
			return # not an error in a restart

		# Try killing the daemon process	
                max_tries = 10
		try:
			while max_tries > 0:
				os.kill(pid, withsignal)
				time.sleep(0.1)
                                max_tries -= 1
		except OSError, err:
			if err.errno == errno.ESRCH:
				if os.path.exists(self.pidfile):
					os.remove(self.pidfile)
                        elif err.errno == errno.EPERM:
                            import subprocess
                            print "It seems you might not have appropriate permissions, try as sudo:"
                            subprocess.call("sudo python -c 'import os; os.kill(%i, %i)'" % (pid, withsignal), shell=True)
			else:
				print str(err)
				sys.exit(1)

	def restart(self):
		"""
		Restart the daemon
		"""
		self.stop()
		self.start()

	def run(self):
		"""
		You should override this method when you subclass Daemon. It will be called after the process has been
		daemonized by start() or restart().
		"""
