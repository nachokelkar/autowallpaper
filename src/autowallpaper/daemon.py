"""
Slightly modified public domain code to create a Daemon process. Credits to Sander Marechal.
Source:
http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
"""

import atexit
import os
import sys
import time
from datetime import datetime
from signal import SIGTERM


class Daemon:
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(
            self,
            pidfile,
            stdout='/tmp/autowallpaper.out',
            stderr='/tmp/autowallpaper.err',
            logfile='/tmp/autowallpaper.log'
        ):
        self.pidfile = pidfile
        self.stdout = stdout
        self.stderr = stderr
        self.logfile = logfile

    def daemonize(self):
        """
        Do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as exception:
            sys.stderr.write(f"Fork #1 failed: {exception.errno} {exception.strerror}\n")
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
        except OSError as exception:
            sys.stderr.write(f"Fork #2 failed: {exception.errno} {exception.strerror}\n")
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        with open(self.stdout, 'a+') as std_out:
            os.dup2(std_out.fileno(), sys.stdout.fileno())
        with open(self.stderr, 'a+') as std_err:
            os.dup2(std_err.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        with open(self.pidfile,'w+') as pidfile:
            pidfile.write(f"{pid}\n")

    def delpid(self):
        """
        Deletes PID file
        """
        os.remove(self.pidfile)

    def start(self, *args, **kwargs):
        """
        Starts the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            with open(self.pidfile,'r') as pidfile:
                pid = int(pidfile.read().strip())
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        if os.path.isfile(self.stdout):
            os.remove(self.stdout)
        if os.path.isfile(self.stderr):
            os.remove(self.stderr)
        if os.path.isfile(self.logfile):
            os.remove(self.logfile)

        # Start the daemon
        self.daemonize()
        self.run(*args, **kwargs)

    def stop(self):
        """
        Stops the daemon
        """
        # Get the pid from the pidfile
        try:
            with open(self.pidfile, 'r') as pidfile:
                pid = int(pidfile.read().strip())
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(err)
                sys.exit(1)

    def restart(self, *args, **kwargs):
        """
        Restarts the daemon
        """
        self.stop()
        self.start(*args, **kwargs)

    def run(self):
        """
        This is the method that will be run after
        `stop()` and `restart()` are called
        """

    def log(self, message: str, log_type: str):
        """
        Output a message into a logfile.
        Path of the file is `logfile` provided during instantiation
        """
        with open(self.logfile, "a+") as logfile:
            logfile.write(f"[{datetime.now()}] {log_type} : " +str(message) +"\n")
