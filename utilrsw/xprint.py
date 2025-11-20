def xprint(msg: str):
  """Print to console and log file based on calling script name.

  The first call from myscript.py will create (or overwrite) myscript.log.

  Subsequent calls will append to myscript.log.

  Example
  --------
  >>> from hxform import xprint
  >>> xprint("Log message")
  """

import threading
_tls = threading.local()
_file_lock = threading.Lock()

def xprint(msg: str):
  import os
  from inspect import stack

  fname = stack()[1][1]
  logfile = os.path.realpath(fname[0:-2]) + "log"

  # per-thread counters dict
  if not hasattr(_tls, "counter"):
    _tls.counter = {}

  if fname not in _tls.counter:
    _tls.counter[fname] = 0

  # ensure the first write for this thread removes existing logfile once,
  # but protect filesystem operations with a lock since files are shared across threads
  if _tls.counter[fname] == 0:
    with _file_lock:
      if os.path.isfile(logfile):
        os.remove(logfile)

  _tls.counter[fname] += 1

  print(msg)

  # appending is typically atomic for small writes on POSIX, but keep lock if you need strict ordering
  with _file_lock:
    with open(logfile, "a") as f:
      f.write(str(msg) + "\n")
