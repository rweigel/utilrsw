def hline(fallback=(80, 24), char="-", indent=0, display=True):
  """Print or return a horizontal line the width of the terminal.
  Parameters
  ----------
  No positional arguments.

  Keyword arguments
  ----------
  fallback : tuple of int, optional
      (columns, rows) used when terminal size cannot be determined. Default (80, 24).
  char : str, optional
      Character repeated to form the line. Default "-".
  indent : int or str, optional
      Number of spaces (int) or string prepended before the line. Default 0.
  display : bool, optional
      If True, prints the line and returns None. If False, returns the line as a string.

  Returns
  -------
  None or str
      None when display=True; the line string when display=False.
  """
  import shutil
  if isinstance(indent, int):
    indent = " " * indent
  columns = shutil.get_terminal_size(fallback=fallback).columns - len(indent)
  line = char * columns 
  if display:
    print(f"{indent}{line}")
  else:
    return f"{indent}{line}"