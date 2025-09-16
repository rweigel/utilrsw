def script_info():
  """Get information about the script that called this function.
  Returns a dictionary with the keys/value pairs of
    - name: The name of the script
    - path: The absolute path of the script
    - dir: The directory of the script
    - line: The line number where the function was called
    - function: The name of the function that called this function
    - module: The name of the module that called this function
    - last_modified: The last modified date of the script
  """
  import os
  import inspect
  import datetime

  frame = inspect.stack()[1]
  calling_function = frame.function
  module = inspect.getmodule(frame[0])
  last_modified = os.path.getmtime(module.__file__)
  last_modified = datetime.datetime.utcfromtimestamp(last_modified).replace(tzinfo=datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
  parent_module = module.__package__ if module and module.__package__ else None
  info = {
    "name": os.path.basename(module.__file__),
    "path": os.path.abspath(module.__file__),
    "dir": os.path.dirname(os.path.abspath(module.__file__)),
    "line": frame[2],
    "function": calling_function,
    "module": parent_module,
    "last_modified": last_modified,
  }
  return info

if __name__ == "__main__":
  import utilrsw
  utilrsw.print_dict(script_info())