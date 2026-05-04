def install(pkg_name, exit_on_failure=True):
  import sys
  import importlib
  import subprocess

  try:
    importlib.import_module(pkg_name)
  except ImportError:
    cmd_list = [sys.executable, '-m', 'pip', 'install', pkg_name]
    print("Executing:", " ".join(cmd_list))
    subprocess.run(cmd_list, check=True)

  if exit_on_failure:
    try:
      importlib.import_module(pkg_name)
    except ImportError:
      print(f"Failed to import {pkg_name} after installation.")
      sys.exit(1)