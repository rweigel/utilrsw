def hline(fallback=(80, 24), char="-", indent=0, display=True):
  import shutil
  if isinstance(indent, int):
    indent = " " * indent
  columns = shutil.get_terminal_size(fallback=fallback).columns - len(indent)
  line = char * columns 
  if display:
    print(f"{indent}{line}")
  else:
    return f"{indent}{line}"