def hline(fallback=(80, 24), char="-", display=True):
  import shutil
  line = char * shutil.get_terminal_size(fallback=fallback).columns
  if display:
    print(line)
  else:
    return line