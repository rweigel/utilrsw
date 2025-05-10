def rm_if_empty(fname):
  import os
  if os.path.exists(fname) and os.path.getsize(fname) == 0:
    os.remove(fname)
