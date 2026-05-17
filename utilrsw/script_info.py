def script_dir(relative=False):
  if relative:
    return script_info(frame_idx=2)['dir_rel']
  else:
    return script_info(frame_idx=2)['dir']

def script_info(frame_idx=1):
  """Get information about the script that called this function.
  Returns a dictionary with the keys/value pairs of
    - name: The name of the script
    - path: The absolute path of the script
    - dir: The directory of the script
    - dir_rel: The directory of the script relative to the current working directory
    - line: The line number where the function was called
    - function: The name of the function that called this function
    - module: The name of the module that called this function
    - last_modified: The last modified date of the script
  """
  import os
  import inspect
  import datetime

  frame = inspect.stack()[frame_idx]

  module = inspect.getmodule(frame[0])

  parent_module = module.__package__ if module and module.__package__ else None
  if parent_module is None and module:
    parent_module = module.__name__

  calling_function = frame.function
  if calling_function == "<module>":
    calling_function = None

  name = None
  path = None
  dir = None
  last_modified = None
  if hasattr(module, '__file__'):
    name = os.path.basename(module.__file__)
    path = os.path.abspath(module.__file__)
    dir = os.path.dirname(path)

    last_modified = os.path.getmtime(module.__file__)
    last_modified = datetime.datetime.utcfromtimestamp(last_modified)
    last_modified = last_modified.replace(tzinfo=datetime.timezone.utc)
    last_modified = last_modified.isoformat().replace('+00:00', 'Z')
  else:
    dir = os.getcwd()

  info = {
    "name": name,
    "path": path,
    "dir": dir,
    "dir_rel": os.path.relpath(dir, os.getcwd()) if dir else None,
    "line": frame[2],
    "function": calling_function,
    "module": parent_module,
    "last_modified": last_modified,
  }
  return info

if __name__ == "__main__":
  import utilrsw
  utilrsw.print_dict(script_info())