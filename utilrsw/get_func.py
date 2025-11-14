def get_func(module_string):
  """
  Returns a function specified by a string path (e.g., "module.submodule.function").
  """
  import importlib
  parts = module_string.split('.')
  module_name = ".".join(parts[:-1])
  function_name = parts[-1]

  try:
    module = importlib.import_module(module_name)
    func = getattr(module, function_name)
    if callable(func):
      return func
    else:
      raise TypeError(f"'{function_name}' in '{module_name}' is not a callable function.")
  except ImportError:
    raise ImportError(f"Module '{module_name}' not found.")
  except AttributeError:
    raise AttributeError(f"Function '{function_name}' not found in module '{module_name}'.")

